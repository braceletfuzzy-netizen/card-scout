FROM mcr.microsoft.com/playwright:v1.63.0-jammy

WORKDIR /usr/src/app

# Install dependencies first for better layer caching
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund

# Copy actor code
COPY main.js ./
COPY actor.json ./

CMD ["node", "main.js"]
