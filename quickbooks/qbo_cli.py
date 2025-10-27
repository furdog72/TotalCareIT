#!/usr/bin/env python3
"""
QuickBooks AI CLI - Local testing interface for the AI agent
"""

import os
import json
import asyncio
from dotenv import load_dotenv
import argparse
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.panel import Panel

# Load environment variables
load_dotenv()

console = Console()


async def run_analysis(question: str, model: str = "claude-3-sonnet-20240229"):
    """
    Run QuickBooks analysis locally
    """
    try:
        # Initialize QuickBooks connection
        from qbo_ai.mcp_server import QBOMCPServer
        from qbo_ai.token_manager import TokenManager
        import boto3

        console.print(Panel.fit("🔧 Initializing QuickBooks Connection", style="cyan"))

        # Check if running locally or with AWS
        use_aws = os.getenv("USE_AWS_SECRETS", "true").lower() == "true"

        if use_aws:
            # Use AWS Secrets Manager
            session = boto3.Session(profile_name='tci')
            secrets_client = session.client('secretsmanager', region_name='us-west-2')
            token_manager = TokenManager(secrets_client=secrets_client)
            console.print("✓ Connected to AWS Secrets Manager", style="green")
        else:
            # Use local tokens file
            console.print("⚠️  Using local token file (not AWS)", style="yellow")
            # You would implement local token loading here if needed

        # Initialize MCP server and get QB client
        server = QBOMCPServer(token_manager=token_manager)
        qb_client = server._get_qb_client()
        qb_client._server = server  # Add reference for token refresh

        console.print("✓ QuickBooks client initialized", style="green")

        # Initialize AI agent
        console.print(Panel.fit(f"🤖 Starting AI Analysis with {model}", style="cyan"))

        from qbo_ai.tools.ai_agent import QuickBooksAIAgent

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            console.print("❌ ANTHROPIC_API_KEY not found in environment", style="red")
            return

        agent = QuickBooksAIAgent(api_key)

        # Run analysis with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(f"[cyan]Analyzing: {question[:50]}...", total=None)

            result = await agent.analyze(
                question=question,
                qb_client=qb_client,
                model=model
            )

            progress.update(task, completed=100)

        # Display results
        if result.get("success"):
            console.print("\n" + "="*60, style="dim")
            console.print(Panel.fit("📊 Analysis Complete", style="green bold"))
            console.print(f"\n**Question:** {result['question']}\n", style="cyan")

            # Display answer as markdown
            answer_md = Markdown(result['answer'])
            console.print(answer_md)

            # Display metadata
            console.print("\n" + "="*60, style="dim")
            console.print(f"Model: {result['model']}", style="dim")
            console.print(f"Tool calls made: {result.get('tool_calls', 0)}", style="dim")
        else:
            console.print(Panel.fit("❌ Analysis Failed", style="red bold"))
            console.print(f"Error: {result.get('error')}", style="red")

        return result

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        import traceback
        console.print(traceback.format_exc(), style="dim red")
        return None


def interactive_mode():
    """
    Run in interactive mode where user can ask multiple questions
    """
    console.print(Panel.fit("🚀 QuickBooks AI Agent - Interactive Mode", style="bold cyan"))
    console.print("Type 'exit' or 'quit' to stop\n")

    model_choices = [
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307"
    ]

    console.print("Available models:")
    for i, m in enumerate(model_choices, 1):
        console.print(f"  {i}. {m}")

    model_choice = Prompt.ask(
        "\nSelect model",
        choices=[str(i) for i in range(1, len(model_choices) + 1)],
        default="1"
    )
    model = model_choices[int(model_choice) - 1]
    console.print(f"Using model: {model}\n", style="green")

    while True:
        question = Prompt.ask("\n💭 Ask a question")

        if question.lower() in ['exit', 'quit']:
            console.print("👋 Goodbye!", style="cyan")
            break

        asyncio.run(run_analysis(question, model))


def main():
    """
    Main CLI entry point
    """
    parser = argparse.ArgumentParser(
        description="QuickBooks AI Agent - Analyze your QuickBooks data with Claude"
    )

    parser.add_argument(
        "question",
        nargs="?",
        help="Question to analyze (if not provided, runs in interactive mode)"
    )

    parser.add_argument(
        "--model",
        default="claude-3-sonnet-20240229",
        help="Claude model to use (default: claude-3-sonnet-20240229)"
    )

    parser.add_argument(
        "--output",
        help="Output file for results (JSON format)"
    )

    args = parser.parse_args()

    if args.question:
        # Single question mode
        result = asyncio.run(run_analysis(args.question, args.model))

        if args.output and result:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
                console.print(f"✓ Results saved to {args.output}", style="green")
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()