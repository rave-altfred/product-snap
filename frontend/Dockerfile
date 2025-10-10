FROM node:18-alpine as development
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

FROM node:18-alpine as build
WORKDIR /app

# Install dependencies first (this layer will be cached unless package.json changes)
COPY package*.json ./
RUN npm ci

# Copy configuration files that affect the build
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY postcss.config.js ./
COPY tailwind.config.js ./
COPY index.html ./

# Copy source code (this will invalidate cache when source changes)
COPY src/ ./src/

# Run the build with optimizations for Docker/emulation
# Skip type checking in Docker (we assume it passes locally)
RUN npm run build:docker || npm run build

FROM nginx:alpine as production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
