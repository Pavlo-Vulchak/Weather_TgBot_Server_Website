# Визначаємо базовий образ для етапу збірки
FROM node:latest

# Встановлюємо робочу директорію в контейнері
WORKDIR /app

# Копіюємо package.json та package-lock.json (якщо він існує)
COPY ./package*.json ./

# Встановлюємо залежності проекту
RUN npm install

# Копіюємо вихідні файли проекту в контейнер
COPY ./. .

# Збираємо додаток для продакшну
RUN npm run build

# Запускаємо npm
CMD npm run start