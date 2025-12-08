#!/bin/bash
# ============================================
# Mom's Club Server Management Script
# ============================================
# Сервер: 109.73.199.102
# Проект: /root/home/momsclub
# ============================================

SERVER="root@109.73.199.102"
PROJECT_PATH="/root/home/momsclub"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_help() {
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Mom's Club Server Management Script        ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Использование:${NC} ./server.sh [команда]"
    echo ""
    echo -e "${YELLOW}Команды:${NC}"
    echo "  status      - Статус бота (systemctl status)"
    echo "  restart     - Перезапустить бота"
    echo "  stop        - Остановить бота"
    echo "  start       - Запустить бота"
    echo "  logs        - Показать последние логи бота"
    echo "  logs-f      - Следить за логами в реальном времени"
    echo "  deploy      - Залить изменения (git pull + restart)"
    echo "  deploy-lib  - Деплой библиотеки (build + restart)"
    echo "  ssh         - Подключиться к серверу"
    echo "  db          - Открыть SQLite базу"
    echo "  copy FILE   - Скопировать файл на сервер"
    echo "  cmd CMD     - Выполнить команду на сервере"
    echo ""
    echo -e "${YELLOW}Примеры:${NC}"
    echo "  ./server.sh status"
    echo "  ./server.sh logs"
    echo "  ./server.sh copy handlers/user_handlers.py"
    echo "  ./server.sh cmd 'sqlite3 momsclub.db \"SELECT COUNT(*) FROM users;\"'"
}

case "$1" in
    status)
        echo -e "${BLUE}📊 Статус бота...${NC}"
        ssh $SERVER "systemctl status telegram-bot"
        ;;
    
    restart)
        echo -e "${YELLOW}🔄 Перезапуск бота...${NC}"
        ssh $SERVER "systemctl restart telegram-bot && sleep 2 && systemctl status telegram-bot | head -15"
        echo -e "${GREEN}✅ Бот перезапущен${NC}"
        ;;
    
    stop)
        echo -e "${RED}⏹ Остановка бота...${NC}"
        ssh $SERVER "systemctl stop telegram-bot && systemctl status telegram-bot | head -5"
        ;;
    
    start)
        echo -e "${GREEN}▶️ Запуск бота...${NC}"
        ssh $SERVER "systemctl start telegram-bot && sleep 2 && systemctl status telegram-bot | head -15"
        ;;
    
    logs)
        echo -e "${BLUE}📜 Последние логи бота...${NC}"
        ssh $SERVER "journalctl -u telegram-bot -n 50 --no-pager"
        ;;
    
    logs-f)
        echo -e "${BLUE}📜 Логи в реальном времени (Ctrl+C для выхода)...${NC}"
        ssh $SERVER "journalctl -u telegram-bot -f"
        ;;
    
    deploy)
        echo -e "${YELLOW}🚀 Деплой изменений...${NC}"
        echo -e "${BLUE}1. Git pull...${NC}"
        ssh $SERVER "cd $PROJECT_PATH && git pull origin main"
        echo -e "${BLUE}2. Перезапуск бота...${NC}"
        ssh $SERVER "systemctl restart telegram-bot && sleep 2 && systemctl status telegram-bot | head -10"
        echo -e "${GREEN}✅ Деплой завершён${NC}"
        ;;
    
    deploy-lib)
        echo -e "${YELLOW}📚 Деплой библиотеки...${NC}"
        echo -e "${BLUE}1. Git pull...${NC}"
        ssh $SERVER "cd /root/home/library_frontend && git pull origin main"
        echo -e "${BLUE}2. npm run build (может занять ~30 сек)...${NC}"
        ssh $SERVER "cd /root/home/library_frontend && npm run build"
        echo -e "${BLUE}3. Перезапуск фронтенда...${NC}"
        ssh $SERVER "systemctl restart library-frontend && sleep 2 && systemctl status library-frontend | head -5"
        echo -e "${GREEN}✅ Библиотека задеплоена${NC}"
        ;;
    
    ssh)
        echo -e "${BLUE}🔗 Подключение к серверу...${NC}"
        ssh $SERVER
        ;;
    
    db)
        echo -e "${BLUE}🗄 Открытие базы данных...${NC}"
        ssh $SERVER "cd $PROJECT_PATH && sqlite3 momsclub.db"
        ;;
    
    copy)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Укажите файл для копирования${NC}"
            echo "Пример: ./server.sh copy handlers/user_handlers.py"
            exit 1
        fi
        echo -e "${BLUE}📤 Копирование $2 на сервер...${NC}"
        scp "$2" "$SERVER:$PROJECT_PATH/$2"
        echo -e "${GREEN}✅ Файл скопирован${NC}"
        ;;
    
    cmd)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Укажите команду${NC}"
            exit 1
        fi
        ssh $SERVER "cd $PROJECT_PATH && $2"
        ;;
    
    *)
        show_help
        ;;
esac
