# Build stage
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Compile the site with node-server preset
ENV NITRO_PRESET=node-server
RUN npm run build

# Run stage
FROM node:20-slim
WORKDIR /app
COPY --from=builder /app/.output .output
ENV PORT=8080
ENV HOST=0.0.0.0
ENV NODE_ENV=production
CMD ["node", ".output/server/index.mjs"]
