#!/usr/bin/env node
import { createOpencode } from "@opencode-ai/sdk"

const TASK = `Implementiere TASK.md - einen Expression Parser Microservice in Java/Spring Boot.
Lies zuerst TASK.md, dann erstelle alle nötigen Java-Klassen und Tests.
Am Ende: ./gradlew build`

async function main() {
  console.log("Starting OpenCode SDK...")

  const { client } = await createOpencode({
    cwd: "/workspace"
  })

  // Create session
  const session = await client.session.create({
    body: { title: "Expression Parser Benchmark" }
  })
  console.log(`Session created: ${session.id}`)

  // Send prompt with GPT-5.1-Codex
  const result = await client.session.prompt({
    path: { id: session.id },
    body: {
      model: {
        providerID: "github-copilot",
        modelID: "gpt-5.1-codex"
      },
      parts: [{ type: "text", text: TASK }]
    }
  })

  console.log("Result:", result)
}

main().catch(console.error)
