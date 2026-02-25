"""
CloudCost.WTF - Your cloud bill analyzer with anger management issues
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
import sys

from cloudcost.azure_analyzer import AzureAnalyzer, MockAzureAnalyzer
from cloudcost.roast_engine import RoastEngine


console = Console()


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    💸 CloudCost.WTF 💸
    
    Your cloud bill analyzer with anger management issues.
    
    Identifies wasteful spending and roasts you for it.
    """
    pass


@cli.command()
@click.option('--subscription-id', '-s', help='Azure subscription ID (uses default if not provided)')
@click.option('--demo', is_flag=True, help='Run in demo mode with mock data (no Azure credentials needed)')
@click.option('--export', type=click.Path(), help='Export results to CSV file')
@click.option('--use-ai/--no-ai', default=True, help='Use local Ollama for AI-powered roasts (default: enabled)')
@click.option('--model', default='mistral', help='Ollama model to use (default: mistral)')
def analyze(subscription_id, demo, export, use_ai, model):
    """
    Analyze Azure subscription for cost waste
    """
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]💸 CLOUDCOST.WTF ANALYSIS 💸[/bold cyan]\n"
        "[dim]Preparing to roast your cloud spending decisions...[/dim]",
        border_style="cyan"
    ))
    console.print("\n")
    
    # Initialize analyzer
    try:
        if demo:
            console.print("[yellow]🎭 Running in DEMO mode with mock data[/yellow]\n")
            analyzer = MockAzureAnalyzer(subscription_id)
        else:
            console.print("[green]🔐 Connecting to Azure...[/green]")
            analyzer = AzureAnalyzer(subscription_id)
    except Exception as e:
        console.print(f"[bold red]❌ Error connecting to Azure:[/bold red] {e}")
        console.print("\n[yellow]💡 Tip: Run with --demo flag to see how it works without Azure credentials[/yellow]")
        console.print("[yellow]   Or run 'az login' to authenticate with Azure[/yellow]\n")
        sys.exit(1)
    
    # Run analysis
    try:
        waste_items = analyzer.analyze()
        total_cost = analyzer.get_total_monthly_cost()
        total_savings = analyzer.estimate_savings(waste_items)
    except Exception as e:
        console.print(f"[bold red]❌ Analysis failed:[/bold red] {e}\n")
        sys.exit(1)
    
    if not waste_items:
        console.print(Panel.fit(
            "[bold green]✅ NO WASTE FOUND[/bold green]\n\n"
            "Your Azure setup is actually... good?\n"
            "I'm impressed. And slightly disappointed I can't roast you.",
            border_style="green"
        ))
        return
    
    # Initialize roast engine
    roaster = RoastEngine(use_ollama=use_ai, model=model)
    
    # Display total cost
    console.print(f"[bold]Your monthly Azure bill:[/bold] [red]${total_cost:,.2f}[/red]\n")
    
    # Create results table
    table = Table(
        title="🔥 TOP OFFENDERS 🔥",
        box=box.HEAVY_HEAD,
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("#", style="dim", width=3)
    table.add_column("Resource", style="bold")
    table.add_column("Type", style="cyan")
    table.add_column("Cost/mo", justify="right", style="red")
    table.add_column("Savings", justify="right", style="green")
    table.add_column("Roast Level", style="yellow")
    
    # Sort by savings (biggest waste first)
    waste_items_sorted = sorted(waste_items, key=lambda x: x.potential_savings, reverse=True)
    
    # Display each waste item
    for idx, item in enumerate(waste_items_sorted, 1):
        roast = roaster.generate_roast(item.waste_type, item.details)
        
        table.add_row(
            str(idx),
            item.resource_name,
            item.resource_type,
            f"${item.current_cost:,.2f}",
            f"${item.potential_savings:,.2f}",
            roast.roast_level
        )
    
    console.print(table)
    console.print("\n")
    
    # Display detailed roasts
    console.print("[bold cyan]📢 DETAILED ROASTS:[/bold cyan]\n")
    
    for idx, item in enumerate(waste_items_sorted, 1):
        roast = roaster.generate_roast(item.waste_type, item.details)
        emoji = roaster.get_emoji_for_severity(item.potential_savings)
        
        # Create roast panel
        roast_text = Text()
        roast_text.append(f"{emoji} {item.resource_name}\n", style="bold")
        roast_text.append(f"   💬 {roast.message}\n", style="yellow")
        roast_text.append(f"   💡 {roast.recommendation}\n", style="green")
        roast_text.append(f"   💰 Save ${item.potential_savings:,.2f}/month\n", style="bold green")
        roast_text.append(f"   🎭 Roast Level: {roast.roast_level}", style="dim")
        
        console.print(Panel(
            roast_text,
            border_style="red" if item.potential_savings > 500 else "yellow",
            padding=(0, 1)
        ))
        console.print("")
    
    # Summary
    yearly_savings = total_savings * 12
    summary_roast = roaster.generate_summary_roast(total_savings, len(waste_items))
    
    console.print(Panel.fit(
        f"[bold]💰 TOTAL SAVINGS POTENTIAL:[/bold]\n\n"
        f"[bold green]${total_savings:,.2f}/month[/bold green] "
        f"[dim]([bold]${yearly_savings:,.2f}/year[/bold])[/dim]\n\n"
        f"{summary_roast}\n\n"
        f"[dim]That's a Tesla Model 3, genius.[/dim]",
        border_style="green",
        title="[bold]SUMMARY[/bold]"
    ))
    
    # Export option
    if export:
        console.print(f"\n[yellow]📄 Exporting results to {export}...[/yellow]")
        _export_to_csv(waste_items, export)
        console.print(f"[green]✅ Export complete![/green]\n")


@cli.command()
def demo():
    """
    Run a quick demo with mock data (no Azure credentials needed)
    """
    ctx = click.get_current_context()
    ctx.invoke(analyze, demo=True)


def _export_to_csv(waste_items, filepath):
    """Export results to CSV"""
    import csv
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Resource', 'Type', 'Current Cost', 'Potential Savings', 'Recommendation'])
        
        for item in waste_items:
            writer.writerow([
                item.resource_name,
                item.resource_type,
                f"${item.current_cost:.2f}",
                f"${item.potential_savings:.2f}",
                item.recommendation
            ])


if __name__ == '__main__':
    cli()
