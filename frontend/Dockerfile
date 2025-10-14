FROM node:18-alpine as development
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

FROM node:18-alpine as build
WORKDIR /app

# Install git for version generation (optional, used if available)
RUN apk add --no-cache git

# Install dependencies first (this layer will be cached unless package.json changes)
COPY frontend/package*.json ./
RUN npm ci

# Copy version generation dependencies
COPY frontend/vite-plugin-version.js ./

# Copy configuration files that affect the build
COPY frontend/tsconfig*.json ./
COPY frontend/vite.config.ts ./
COPY frontend/postcss.config.js ./
COPY frontend/tailwind.config.js ./
COPY frontend/index.html ./

# Copy public folder (static assets like favicon)
COPY frontend/public/ ./public/

# Copy source code (this will invalidate cache when source changes)
COPY frontend/src/ ./src/

# Mark directory as safe for git operations
RUN git config --global --add safe.directory /app

# Run the build with type checking
# This will fail if there are TypeScript errors
RUN npm run build

FROM nginx:alpine as production
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
