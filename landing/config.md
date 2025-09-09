# Aaadviser Landing Page - Конфигурационные файлы

## Nginx конфигурация (nginx.conf)

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    root /var/www/aaadvisor-landing;
    index index.html;

    # Основные настройки
    charset utf-8;
    client_max_body_size 10M;

    # Обработка статических файлов
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Кэширование статических файлов
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
    }

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        application/xml
        image/svg+xml;

    # Заголовки безопасности
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://telegram.org; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://www.google-analytics.com;" always;

    # Запрет доступа к скрытым файлам
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Логирование
    access_log /var/log/nginx/aaadvisor-landing.access.log;
    error_log /var/log/nginx/aaadvisor-landing.error.log;
}

# HTTPS редирект
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS конфигурация
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    root /var/www/aaadvisor-landing;
    index index.html;

    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Остальные настройки такие же как выше
    charset utf-8;
    client_max_body_size 10M;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
    }

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        application/xml
        image/svg+xml;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://telegram.org; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://www.google-analytics.com;" always;

    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    access_log /var/log/nginx/aaadvisor-landing.access.log;
    error_log /var/log/nginx/aaadvisor-landing.error.log;
}
```

## Apache .htaccess

```apache
# Включение модулей
RewriteEngine On

# Редирект на HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Удаление www
RewriteCond %{HTTP_HOST} ^www\.(.+)$ [NC]
RewriteRule ^(.*)$ https://%1/$1 [R=301,L]

# Обработка SPA роутинга
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.html [QSA,L]

# Кэширование статических файлов
<IfModule mod_expires.c>
    ExpiresActive on
    
    # Изображения
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/ico "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
    ExpiresByType image/webp "access plus 1 year"
    
    # CSS и JavaScript
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType text/javascript "access plus 1 year"
    
    # Шрифты
    ExpiresByType font/woff "access plus 1 year"
    ExpiresByType font/woff2 "access plus 1 year"
    ExpiresByType application/font-woff "access plus 1 year"
    ExpiresByType application/font-woff2 "access plus 1 year"
    
    # HTML
    ExpiresByType text/html "access plus 1 hour"
</IfModule>

# Gzip сжатие
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
    AddOutputFilterByType DEFLATE application/json
    AddOutputFilterByType DEFLATE image/svg+xml
</IfModule>

# Заголовки безопасности
<IfModule mod_headers.c>
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set X-Content-Type-Options "nosniff"
    Header always set Referrer-Policy "no-referrer-when-downgrade"
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://telegram.org; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://www.google-analytics.com;"
</IfModule>

# Запрет доступа к скрытым файлам
<FilesMatch "^\.">
    Order allow,deny
    Deny from all
</FilesMatch>

# Запрет доступа к конфигурационным файлам
<FilesMatch "\.(htaccess|htpasswd|ini|log|sh|inc|bak)$">
    Order allow,deny
    Deny from all
</FilesMatch>
```

## Docker конфигурация

### Dockerfile
```dockerfile
# Используем официальный образ Nginx
FROM nginx:alpine

# Копируем файлы лендинга
COPY . /usr/share/nginx/html/

# Копируем конфигурацию Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Создаем пользователя для безопасности
RUN addgroup -g 1001 -S nginx && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Устанавливаем права
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Открываем порт
EXPOSE 80 443

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  aaadvisor-landing:
    build: .
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped
    environment:
      - NGINX_HOST=your-domain.com
      - NGINX_PORT=80
    networks:
      - web

networks:
  web:
    external: true
```

## Netlify конфигурация

### netlify.toml
```toml
[build]
  publish = "."
  command = ""

[build.environment]
  NODE_VERSION = "16"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "SAMEORIGIN"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "no-referrer-when-downgrade"
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://telegram.org; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://www.google-analytics.com;"

[[headers]]
  for = "*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "*.png"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "*.jpg"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "*.svg"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

## Vercel конфигурация

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "**/*",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "SAMEORIGIN"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Referrer-Policy",
          "value": "no-referrer-when-downgrade"
        },
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://telegram.org; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://www.google-analytics.com;"
        }
      ]
    },
    {
      "source": "/(.*\\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot))",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

## GitHub Actions для автоматического развертывания

### .github/workflows/deploy.yml
```yaml
name: Deploy Aaadviser Landing

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Build
      run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Netlify
      uses: nwtgck/actions-netlify@v2.0
      with:
        publish-dir: './landing'
        production-branch: main
        github-token: ${{ secrets.GITHUB_TOKEN }}
        deploy-message: "Deploy from GitHub Actions"
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
    
    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        working-directory: ./landing
```

## Скрипты для развертывания

### deploy.sh
```bash
#!/bin/bash

# Скрипт для развертывания на VPS

set -e

echo "🚀 Начинаем развертывание Aaadviser Landing Page..."

# Проверяем наличие необходимых файлов
if [ ! -f "index.html" ]; then
    echo "❌ Ошибка: index.html не найден"
    exit 1
fi

# Создаем резервную копию
echo "📦 Создаем резервную копию..."
sudo cp -r /var/www/aaadvisor-landing /var/www/aaadvisor-landing.backup.$(date +%Y%m%d_%H%M%S)

# Копируем файлы
echo "📁 Копируем файлы..."
sudo cp -r . /var/www/aaadvisor-landing/

# Устанавливаем права
echo "🔐 Устанавливаем права доступа..."
sudo chown -R www-data:www-data /var/www/aaadvisor-landing/
sudo chmod -R 755 /var/www/aaadvisor-landing/

# Проверяем конфигурацию Nginx
echo "🔍 Проверяем конфигурацию Nginx..."
sudo nginx -t

# Перезапускаем Nginx
echo "🔄 Перезапускаем Nginx..."
sudo systemctl reload nginx

# Проверяем статус
echo "✅ Проверяем статус сервисов..."
sudo systemctl status nginx --no-pager

echo "🎉 Развертывание завершено успешно!"
echo "🌐 Сайт доступен по адресу: https://your-domain.com"
```

### install.sh
```bash
#!/bin/bash

# Скрипт для первоначальной установки

set -e

echo "🔧 Установка Aaadviser Landing Page..."

# Обновляем систему
echo "📦 Обновляем систему..."
sudo apt update && sudo apt upgrade -y

# Устанавливаем Nginx
echo "🌐 Устанавливаем Nginx..."
sudo apt install -y nginx

# Устанавливаем SSL сертификаты
echo "🔒 Устанавливаем Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Создаем директорию
echo "📁 Создаем директорию..."
sudo mkdir -p /var/www/aaadvisor-landing

# Копируем файлы
echo "📁 Копируем файлы..."
sudo cp -r . /var/www/aaadvisor-landing/

# Устанавливаем права
echo "🔐 Устанавливаем права доступа..."
sudo chown -R www-data:www-data /var/www/aaadvisor-landing/
sudo chmod -R 755 /var/www/aaadvisor-landing/

# Копируем конфигурацию Nginx
echo "⚙️ Настраиваем Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/aaadvisor-landing
sudo ln -sf /etc/nginx/sites-available/aaadvisor-landing /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
echo "🔍 Проверяем конфигурацию..."
sudo nginx -t

# Перезапускаем Nginx
echo "🔄 Перезапускаем Nginx..."
sudo systemctl restart nginx

# Настраиваем автозапуск
echo "🚀 Настраиваем автозапуск..."
sudo systemctl enable nginx

echo "✅ Установка завершена!"
echo "🌐 Сайт доступен по адресу: http://your-domain.com"
echo "🔒 Для настройки SSL выполните: sudo certbot --nginx -d your-domain.com"
```

## Мониторинг и логирование

### logrotate конфигурация
```bash
# /etc/logrotate.d/aaadvisor-landing
/var/log/nginx/aaadvisor-landing.*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 `cat /var/run/nginx.pid`
        fi
    endscript
}
```

### systemd сервис (опционально)
```ini
# /etc/systemd/system/aaadvisor-landing.service
[Unit]
Description=Aaadviser Landing Page
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/aaadvisor-landing
ExecStart=/usr/bin/nginx -g "daemon off;"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

**Примечание:** Замените `your-domain.com` на ваш реальный домен во всех конфигурационных файлах.
