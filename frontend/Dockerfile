FROM node:24-slim

ENV PNPM_HOME="/home/node/.local/share/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
ENV CI=true

RUN corepack enable

WORKDIR /app
RUN chown node:node /app

USER node

COPY --chown=node:node pnpm-lock.yaml pnpm-workspace.yaml* ./

RUN --mount=type=cache,id=pnpm,target=/home/node/.local/share/pnpm/store \
    pnpm fetch

COPY --chown=node:node package.json ./

RUN --mount=type=cache,id=pnpm,target=/home/node/.local/share/pnpm/store \
    pnpm install

COPY --chown=node:node . .

EXPOSE 3000

CMD ["pnpm", "dev"]
