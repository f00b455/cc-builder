ARG BASE_IMAGE=cc-builder:base
FROM ${BASE_IMAGE}

LABEL description="Claude Code TDD Builder - Go"

ENV CC_DEFAULT_LANGUAGE=go

# === GO (from official image, multi-arch) ===
USER root
COPY --from=golang:1.22-bookworm /usr/local/go /usr/local/go

ENV PATH="/usr/local/go/bin:/home/builder/go/bin:$PATH"
ENV GOPATH="/home/builder/go"

# === GODOG (Cucumber for Go) - install as builder ===
USER builder
RUN go install github.com/cucumber/godog/cmd/godog@latest

# === VERIFY ===
RUN go version && godog --version

# === TEMPLATES ===
USER root
COPY go/templates/ /opt/go-templates/
COPY go/bin/init-go-project /usr/local/bin/init-go-project
RUN chmod +x /usr/local/bin/init-go-project

USER root
