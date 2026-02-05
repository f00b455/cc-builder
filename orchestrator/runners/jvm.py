"""
JVM BDD runner for Java/Kotlin using Cucumber.
"""

import re
from typing import Tuple
from pathlib import Path

from .base import BaseRunner


class JVMRunner(BaseRunner):
    """
    JVM (Java/Kotlin) language runner.

    Uses:
    - Cucumber-JVM for BDD tests
    - JaCoCo for coverage measurement
    - Gradle as build tool
    """

    @property
    def name(self) -> str:
        return "jvm"

    @property
    def bdd_framework(self) -> str:
        return "cucumber"

    def _is_gradle_kotlin(self) -> bool:
        """Check if using Gradle Kotlin DSL."""
        return Path('build.gradle.kts').exists()

    def _is_gradle(self) -> bool:
        """Check if using Gradle."""
        return Path('build.gradle').exists() or Path('build.gradle.kts').exists()

    def _is_maven(self) -> bool:
        """Check if using Maven."""
        return Path('pom.xml').exists()

    def _ensure_gradlew(self) -> None:
        """Generate Gradle wrapper if missing."""
        if not Path('gradlew').exists() and self._is_gradle():
            self.run_command(['gradle', 'wrapper', '--gradle-version', '8.5'])

    def init_project(self) -> None:
        """Run init-jvm-project if available and project not yet initialized."""
        import shutil
        init_script = shutil.which('init-jvm-project')
        if init_script and not self._is_gradle() and not self._is_maven():
            result = self.run_command(['init-jvm-project'])
            if result.returncode == 0:
                print("  Initialized JVM project from templates")
        self._ensure_gradlew()

    def run_bdd(self) -> Tuple[bool, str]:
        """
        Run Cucumber BDD tests.

        Returns:
            Tuple of (all_passed, output)
        """
        if not self.features_exist():
            return False, "No feature files found in features/"

        self._ensure_gradlew()

        if self._is_gradle():
            # Run cucumber via Gradle
            result = self.run_command(['./gradlew', 'cucumber', '--info'])
        elif self._is_maven():
            # Run cucumber via Maven
            result = self.run_command(['mvn', 'test', '-Dcucumber'])
        else:
            return False, "No build tool found (need build.gradle or pom.xml)"

        output = result.stdout + result.stderr
        success = result.returncode == 0

        # Check for undefined steps
        if 'undefined' in output.lower() or 'pending' in output.lower():
            success = False

        return success, output

    def run_e2e(self) -> Tuple[bool, str]:
        """No E2E tests for JVM runner."""
        return True, ""

    def measure_coverage(self) -> float:
        """
        Measure test coverage using JaCoCo.

        Returns:
            Coverage percentage
        """
        self._ensure_gradlew()

        if self._is_gradle():
            # Run tests with JaCoCo
            result = self.run_command([
                './gradlew', 'test', 'jacocoTestReport'
            ])

            if result.returncode != 0:
                print(f"Warning: gradle test failed")
                return 0.0

            # Parse JaCoCo report
            return self._parse_jacoco_report()

        elif self._is_maven():
            result = self.run_command([
                'mvn', 'test', 'jacoco:report'
            ])

            if result.returncode != 0:
                return 0.0

            return self._parse_jacoco_report()

        return 0.0

    def _parse_jacoco_report(self) -> float:
        """Parse JaCoCo XML or HTML report for coverage percentage."""
        # Try XML report first
        xml_paths = [
            Path('build/reports/jacoco/test/jacocoTestReport.xml'),
            Path('target/site/jacoco/jacoco.xml'),
        ]

        for xml_path in xml_paths:
            if xml_path.exists():
                return self._parse_jacoco_xml(xml_path)

        # Try HTML report
        html_paths = [
            Path('build/reports/jacoco/test/html/index.html'),
            Path('target/site/jacoco/index.html'),
        ]

        for html_path in html_paths:
            if html_path.exists():
                return self._parse_jacoco_html(html_path)

        # Fallback: parse Gradle output
        return 0.0

    def _parse_jacoco_xml(self, path: Path) -> float:
        """Parse JaCoCo XML report."""
        import xml.etree.ElementTree as ET

        try:
            tree = ET.parse(path)
            root = tree.getroot()

            # Use the report-level (last) instruction counter for overall coverage
            counters = root.findall('.//counter[@type="INSTRUCTION"]')
            if counters:
                # The last counter is the report-level total
                counter = counters[-1]
                missed = int(counter.get('missed', 0))
                covered = int(counter.get('covered', 0))
                total = missed + covered
                if total > 0:
                    return (covered / total) * 100

        except Exception as e:
            print(f"Warning: Could not parse JaCoCo XML: {e}")

        return 0.0

    def _parse_jacoco_html(self, path: Path) -> float:
        """Parse JaCoCo HTML report for total coverage."""
        try:
            content = path.read_text()
            # Look for total coverage percentage
            match = re.search(r'Total.*?(\d+)\s*%', content, re.DOTALL)
            if match:
                return float(match.group(1))
        except Exception as e:
            print(f"Warning: Could not parse JaCoCo HTML: {e}")

        return 0.0

    def build(self) -> Tuple[bool, str]:
        """Build executable JAR (Spring Boot bootJar)."""
        self._ensure_gradlew()

        if self._is_gradle():
            result = self.run_command(['./gradlew', 'clean', 'bootJar'], timeout=300)
            if result.returncode != 0:
                # Fallback to regular build if bootJar not configured
                result = self.run_command(['./gradlew', 'clean', 'build', '-x', 'test'], timeout=300)
                if result.returncode != 0:
                    return False, result.stderr or result.stdout

            # Verify JAR exists
            jar_files = list(Path('build/libs').glob('*.jar')) if Path('build/libs').exists() else []
            if not jar_files:
                return False, "Build succeeded but no JAR found in build/libs/"

            # Prefer the executable (non-plain) JAR
            exec_jars = [j for j in jar_files if '-plain' not in j.name]
            jar = exec_jars[0] if exec_jars else jar_files[0]
            return True, f"Executable JAR: {jar} ({jar.stat().st_size // 1024}KB)"

        elif self._is_maven():
            result = self.run_command(['mvn', 'package', '-DskipTests'], timeout=300)
            if result.returncode != 0:
                return False, result.stderr or result.stdout
            target = Path('target')
            jar_files = list(target.glob('*.jar')) if target.exists() else []
            if jar_files:
                jar = jar_files[0]
                return True, f"Executable JAR: {jar} ({jar.stat().st_size // 1024}KB)"
            return False, "Build succeeded but no JAR found in target/"

        return False, "No build tool found"

    def run_lint(self) -> Tuple[bool, str]:
        """Run compilation check (Java/Kotlin doesn't have a separate linter by default)."""
        self._ensure_gradlew()
        if self._is_gradle():
            result = self.run_command(['./gradlew', 'compileJava', 'compileTestJava'], timeout=120)
            if result.returncode != 0:
                return False, result.stderr or result.stdout
            return True, "Compilation OK"
        return True, "No lint configured"

    def init_gradle_project(self, language: str = 'java') -> None:
        """Initialize Gradle project if not exists."""
        if self._is_gradle() or self._is_maven():
            return

        # Create basic build.gradle.kts
        build_file = Path('build.gradle.kts')
        build_file.write_text(f'''plugins {{
    {"kotlin(\"jvm\") version \"1.9.22\"" if language == "kotlin" else "java"}
    jacoco
}}

repositories {{
    mavenCentral()
}}

dependencies {{
    testImplementation("io.cucumber:cucumber-java:7.15.0")
    testImplementation("io.cucumber:cucumber-junit-platform-engine:7.15.0")
    testImplementation("org.junit.platform:junit-platform-suite:1.10.2")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
}}

tasks.test {{
    useJUnitPlatform()
}}

tasks.register<Test>("cucumber") {{
    useJUnitPlatform {{
        includeTags("cucumber")
    }}
}}
''')
        print("Created build.gradle.kts")
