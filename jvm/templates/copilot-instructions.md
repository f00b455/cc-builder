# Spring Boot Microservice

Java 21 + Spring Boot 3.2+, Spring Data JPA, Gradle Kotlin DSL, JaCoCo 80% coverage.

## Structure
- `src/main/java/de/prehcm/` — application code
- `controller/` — `@RestController` returning `ResponseEntity<>`
- `service/` — `@Service` business logic (constructor injection only)
- `repository/` — `JpaRepository<Entity, UUID>` interfaces
- `model/` — JPA entities with UUID keys, `LocalDateTime` timestamps
- `dto/` — request/response DTOs with Jakarta validation
- `exception/` — `GlobalExceptionHandler` + custom exceptions
- `features/*.feature` + `features/steps/*StepDefs.java` — Cucumber BDD

## Rules
- Constructor injection — NEVER `@Autowired` on fields
- DTOs at boundaries — controllers never expose entities
- REST: plural nouns (`/api/v1/notes`), proper HTTP methods/status codes
- `@Valid` on request bodies, `@Transactional` on write services
- Entities: `@Entity`, `@Id`, `@GeneratedValue`, `@Column`
- `@PrePersist`/`@PreUpdate` for audit fields
- H2 for tests, PostgreSQL for production
- Actuator health probes: `/actuator/health/{liveness,readiness}`
- Every dependency must be in `build.gradle.kts` first
- Pure methods, single responsibility, max 20-30 lines, early returns

## Testing
- 80% coverage (JaCoCo), `@WebMvcTest` for controllers, `@DataJpaTest` for repos
- Cucumber BDD: all scenarios must pass
- Use `@SpringBootTest` sparingly

## Commands
- `./gradlew build` — build + tests
- `./gradlew test` — unit tests
- `./gradlew cucumber` — BDD
- `./gradlew jacocoTestReport` — coverage
- `./gradlew bootRun` — run locally
