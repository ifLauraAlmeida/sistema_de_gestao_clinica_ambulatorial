FROM node:22-alpine

# Usuário sem privilégios (uid 1000): arquivos gerados no volume montado
# (build, cache) ficam com o mesmo dono do usuário do host.
WORKDIR /app
RUN chown node:node /app
USER node

COPY --chown=node:node package.json package-lock.json ./
RUN npm ci

COPY --chown=node:node . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
