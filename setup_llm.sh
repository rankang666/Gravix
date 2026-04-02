#!/bin/bash
# Gravix LLM Setup Script

echo "================================"
echo "Gravix LLM Configuration Setup"
echo "================================"
echo ""

# Check if .env file exists
if [ -f .env ]; then
    echo "Found existing .env file"
    source .env
else
    echo "Creating new .env file"
    touch .env
fi

echo ""
echo "Please select your LLM provider:"
echo "1) Claude (Anthropic) - Recommended"
echo "2) OpenAI"
echo "3) Skip (Keep current configuration)"
echo ""
read -p "Enter your choice (1-3): " provider_choice

case $provider_choice in
    1)
        echo ""
        echo "Setting up Claude (Anthropic)..."
        echo ""

        if [ -z "$ANTHROPIC_API_KEY" ]; then
            echo "Enter your Anthropic API Key:"
            echo "(Get it from: https://console.anthropic.com/)"
            read -s ANTHROPIC_API_KEY
            echo ""
        else
            echo "Using existing ANTHROPIC_API_KEY"
        fi

        # Update .env
        echo "LLM_PROVIDER=claude" > .env
        echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" >> .env

        # Optionally set model
        echo ""
        echo "Select Claude model (default: claude-3-5-sonnet-20241022):"
        echo "1) claude-3-5-sonnet-20241022 (Recommended)"
        echo "2) claude-3-5-haiku-20241022"
        echo "3) claude-3-opus-20240229"
        echo "4) Use default"
        read -p "Enter your choice (1-4): " model_choice

        case $model_choice in
            1) echo "LLM_MODEL=claude-3-5-sonnet-20241022" >> .env ;;
            2) echo "LLM_MODEL=claude-3-5-haiku-20241022" >> .env ;;
            3) echo "LLM_MODEL=claude-3-opus-20240229" >> .env ;;
            4) echo "LLM_MODEL=claude-3-5-sonnet-20241022" >> .env ;;
        esac

        echo ""
        echo "✅ Claude configuration saved to .env"
        ;;

    2)
        echo ""
        echo "Setting up OpenAI..."
        echo ""

        if [ -z "$OPENAI_API_KEY" ]; then
            echo "Enter your OpenAI API Key:"
            echo "(Get it from: https://platform.openai.com/api-keys)"
            read -s OPENAI_API_KEY
            echo ""
        else
            echo "Using existing OPENAI_API_KEY"
        fi

        # Update .env
        echo "LLM_PROVIDER=openai" > .env
        echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> .env

        # Optionally set model
        echo ""
        echo "Select OpenAI model (default: gpt-4o):"
        echo "1) gpt-4o (Recommended)"
        echo "2) gpt-4o-mini"
        echo "3) gpt-4-turbo"
        echo "4) gpt-3.5-turbo"
        echo "5) Use default"
        read -p "Enter your choice (1-5): " model_choice

        case $model_choice in
            1) echo "LLM_MODEL=gpt-4o" >> .env ;;
            2) echo "LLM_MODEL=gpt-4o-mini" >> .env ;;
            3) echo "LLM_MODEL=gpt-4-turbo" >> .env ;;
            4) echo "LLM_MODEL=gpt-3.5-turbo" >> .env ;;
            5) echo "LLM_MODEL=gpt-4o" >> .env ;;
        esac

        echo ""
        echo "✅ OpenAI configuration saved to .env"
        ;;

    3)
        echo ""
        echo "Skipping LLM configuration"
        echo ""
        exit 0
        ;;

    *)
        echo ""
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "================================"
echo "Configuration Summary"
echo "================================"
cat .env
echo ""
echo "================================"
echo ""

# Ask if user wants to restart the service
echo "Do you want to restart Gravix service now?"
read -p "Restart now? (y/n): " restart_choice

if [ "$restart_choice" = "y" ] || [ "$restart_choice" = "Y" ]; then
    echo ""
    echo "Restarting Gravix service..."

    # Kill existing service
    pkill -f "python.*run_all.py" 2>/dev/null
    sleep 2

    # Load environment and start service
    export $(cat .env | xargs)
    /opt/miniconda3/envs/owner/bin/python run_all.py
else
    echo ""
    echo "To start Gravix with LLM support, run:"
    echo ""
    echo "  source .env"
    echo "  /opt/miniconda3/envs/owner/bin/python run_all.py"
    echo ""
fi
