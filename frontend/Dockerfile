FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install --no-audit --no-fund; fi

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
