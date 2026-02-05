# Spring Boot Microservice

## Tech Stack
- **Language**: Java 21 (LTS)
- **Framework**: Spring Boot 3.2+
- **ORM**: Spring Data JPA / Hibernate
- **API**: REST (Spring Web)
- **Testing**: JUnit 5, Cucumber-JVM, MockMvc
- **Coverage**: JaCoCo (80% minimum)
- **Build**: Gradle (Kotlin DSL)
- **Monitoring**: Spring Actuator

## Project Structure
```
src/
├── main/
│   ├── java/de/prehcm/
│   │   ├── Application.java          # @SpringBootApplication
│   │   ├── config/                   # Configuration classes
│   │   │   └── WebConfig.java
│   │   ├── controller/               # REST controllers
│   │   │   └── *Controller.java
│   │   ├── service/                  # Business logic
│   │   │   └── *Service.java
│   │   ├── repository/               # Data access (JPA)
│   │   │   └── *Repository.java
│   │   ├── model/                    # JPA entities
│   │   │   └── *.java
│   │   ├── dto/                      # Request/Response DTOs
│   │   │   └── *Dto.java
│   │   └── exception/                # Error handling
│   │       ├── GlobalExceptionHandler.java
│   │       └── ResourceNotFoundException.java
│   └── resources/
│       └── application.yaml
├── test/
│   └── java/de/prehcm/
│       ├── controller/               # MockMvc tests
│       ├── service/                  # Unit tests
│       └── repository/               # @DataJpaTest
features/
├── *.feature                         # Gherkin scenarios
└── steps/
    └── *StepDefs.java               # Cucumber step definitions
build.gradle.kts
```

## Critical Rules

### Clean Code Principles
- **Pure functions** - No side effects in service methods where possible
- **Single Responsibility** - One class = one purpose
- **Constructor injection** - NEVER use @Autowired on fields
- **DTOs at boundaries** - Controllers receive/return DTOs, NOT entities
- **Small methods** - Max 20-30 lines
- **Early returns** - Avoid deep nesting
- **Named constants** - No magic numbers/strings

### Spring Boot Conventions
- Use `@RestController` + `@RequestMapping` for REST endpoints
- Use `@Service` for business logic
- Use `@Repository` (Spring Data JPA interfaces) for data access
- Use `@Validated` + Jakarta Bean Validation on DTOs
- Return `ResponseEntity<>` from controllers
- Use `@Transactional` on service methods that modify data

### REST API Design
- Use proper HTTP methods: GET, POST, PUT, DELETE, PATCH
- Use proper HTTP status codes: 200, 201, 204, 400, 404, 409, 500
- Use plural nouns for endpoints: `/api/v1/notes`, NOT `/api/v1/note`
- Return consistent error responses with `GlobalExceptionHandler`
- Use `@Valid` on request body parameters

### JPA / Hibernate
- Entities use `@Entity`, `@Id`, `@GeneratedValue`
- Use `@Column` for explicit mapping
- Use `LocalDateTime` for timestamps (NOT `Date`)
- Use `@PrePersist` / `@PreUpdate` for audit fields
- Repositories extend `JpaRepository<Entity, UUID>`
- Use UUID as primary key type

### Kubernetes Readiness
- Health endpoint via Spring Actuator: `/actuator/health`
- Liveness: `/actuator/health/liveness`
- Readiness: `/actuator/health/readiness`
- Graceful shutdown enabled
- No hardcoded URLs - use environment variables / Spring profiles

### Dependencies
- EVERY dependency you use MUST be in build.gradle.kts FIRST
- Prefer Spring Boot starters over individual dependencies
- Do NOT add dependencies you don't need
- Use Spring Boot BOM for version management

### Database
- Use H2 in-memory for tests
- Use PostgreSQL profile for production
- Flyway or Liquibase for migrations (if needed)
- application.yaml configures datasource

## Commands
```bash
./gradlew build              # Build + tests
./gradlew test               # Unit tests
./gradlew jacocoTestReport   # Coverage report
./gradlew cucumber           # BDD tests
./gradlew bootRun            # Run locally
./gradlew bootJar            # Build executable JAR
./gradlew clean build        # Clean build
```

## Testing Requirements
- Unit tests: 80% coverage minimum (JaCoCo)
- BDD tests: All Cucumber scenarios must pass
- Integration tests: MockMvc for controller layer
- Use `@SpringBootTest` sparingly (prefer sliced tests)
- Use `@WebMvcTest` for controller tests
- Use `@DataJpaTest` for repository tests

## When Extending This Codebase
1. Read existing code first - understand patterns
2. Follow existing package structure
3. Add tests for new code
4. Run `./gradlew clean build` before committing
