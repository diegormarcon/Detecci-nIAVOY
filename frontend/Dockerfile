FROM node:18-alpine

WORKDIR /app

# Instalar dependencias del sistema
RUN apk add --no-cache python3 make g++

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias con timeout y reintentos
RUN npm config set fetch-retries 3 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm install --legacy-peer-deps || npm install --force

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 3050

# Comando de desarrollo
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3050"]

