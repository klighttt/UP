FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY module_c_results.js .
EXPOSE 3000
CMD ["node", "module_c_results.js"]