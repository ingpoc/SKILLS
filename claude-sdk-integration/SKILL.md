# Claude Agent SDK Integration Skill

Comprehensive guide for integrating Claude Agent SDK with robo-trader's paper trading system.

## Agent SDK Architecture

### Component Overview

```
Claude Agent SDK Bot (running in .claude/ context)
    ↓
ClaudeAgentService (event handler)
    ↓
ClaudeAgentCoordinator (orchestrator)
    ├─ AgentSessionCoordinator (session management)
    │  ├─ MorningSessionCoordinator (strategy generation)
    │  └─ EveningSessionCoordinator (performance review)
    ├─ AgentToolCoordinator (MCP tools)
    └─ AgentPromptBuilder (system prompts)
```

### Key Concepts

**Agent Profiles**: Defined in `.claude/agents/*.md` for SDK bot discovery
**Skills**: Reusable knowledge in `.claude/skills/*/SKILL.md`
**MCP Tools**: Python functions decorated with `@tool` for Claude to call
**Sessions**: Morning prep (strategy gen) + Evening review (performance analysis)

## Creating Agent Profiles

### Agent Profile Location
`.claude/agents/[agent-name].md`

### Agent Profile Structure

```markdown
---
name: technical-analyst
description: Analyzes stocks using technical indicators (RSI, MACD, Moving Averages). Identifies momentum, breakouts, and trend reversals for paper trading recommendations.
model: sonnet
color: blue
tools: Read, Bash
---

You are a technical analyst specializing in Indian equity markets (NSE/BSE).

## Your Expertise
- Technical indicators: RSI, MACD, Bollinger Bands, Moving Averages
- Chart patterns: Head & shoulders, triangles, flags
- Volume analysis
- Support/resistance levels

## Your Role in Paper Trading
1. Analyze charts for entry/exit signals
2. Recommend trades with specific stop loss/target levels
3. Identify high-probability setups
4. Monitor open positions for technical exits

## Tools Available
You can execute paper trades, check balance, analyze positions via MCP tools.

## Risk Guidelines
- Max risk per trade: 2% of capital
- R:R minimum: 1:2
- Stop loss mandatory on all trades
- Position size: Max 15% of portfolio

[Continue with detailed instructions...]
```

### Agent Types Needed

| Agent | Role | Focus |
|-------|------|-------|
| `technical-analyst` | Chart analysis | RSI, MACD, patterns |
| `fundamental-screener` | Financial health | P/E, debt, earnings growth |
| `risk-manager` | Portfolio risk | Exposure, correlation, drawdown |
| `portfolio-analyzer` | Performance review | Returns, Sharpe, sector allocation |
| `market-monitor` | Real-time alerts | Volume spikes, breakouts |
| `strategy-optimizer` | Strategy tuning | Parameter optimization |

## Skill Integration

### Skill Location
`.claude/skills/[skill-name]/SKILL.md`

### Archived Skills to Integrate

**Found in**: `docs/agent-sdk-skills-archive/`

1. **Trade Execution Skill** - Pre-trade validation, execution rules
2. **Portfolio Analysis Skill** - Risk assessment, Indian market focus
3. **Risk Management Skill** - Position sizing, capital preservation
4. **Market Monitor Skill** - Real-time awareness, alert conditions

### Loading Skills in Coordinators

```python
# In AgentPromptBuilder.build_system_prompt()
def build_system_prompt(self, session_type: str, context: dict) -> str:
    # Load skill content
    trade_execution_skill = self._load_skill("trade-execution")
    risk_management_skill = self._load_skill("risk-management")

    prompt = f"""
You are a trading bot following these guidelines:

{trade_execution_skill}

{risk_management_skill}

Current context:
- Account balance: ₹{context['balance']}
- Open positions: {len(context['positions'])}
- Available capital: ₹{context['buying_power']}
...
"""
    return prompt
```

## MCP Tools Pattern

### Tool Registration

```python
# In src/core/coordinators/agent/agent_tool_coordinator.py
from anthropic_mcp import mcp_server

@mcp_server.tool()
async def execute_trade(
    symbol: str,
    action: str,  # "BUY" or "SELL"
    quantity: int,
    stop_loss: float = None,
    target: float = None,
    strategy: str = "manual"
) -> dict:
    """
    Execute paper trade with risk validation.

    Args:
        symbol: Stock symbol (e.g., "RELIANCE")
        action: Trade action ("BUY" or "SELL")
        quantity: Number of shares
        stop_loss: Stop loss price (optional)
        target: Target price (optional)
        strategy: Strategy tag for performance tracking

    Returns:
        {"success": bool, "trade_id": str, "message": str}
    """
    # Validation
    trade_validator = container.resolve("trade_validator")
    validation_result = await trade_validator.validate(
        symbol=symbol,
        action=action,
        quantity=quantity,
        stop_loss=stop_loss
    )

    if not validation_result.is_valid:
        return {
            "success": False,
            "message": validation_result.error_message
        }

    # Execute via service
    paper_trade_executor = container.resolve("paper_trade_executor")
    trade_result = await paper_trade_executor.execute_buy_trade(
        symbol=symbol,
        quantity=quantity,
        stop_loss=stop_loss,
        target=target,
        strategy=strategy
    )

    return {
        "success": True,
        "trade_id": trade_result["trade_id"],
        "message": f"Bought {quantity} {symbol} at ₹{trade_result['price']}"
    }
```

### Progressive Discovery Pattern

**Send tool names only upfront, descriptions on-demand:**

```python
# In create_sdk_mcp_server()
tools = [
    {"name": "execute_trade"},
    {"name": "close_position"},
    {"name": "check_balance"},
    {"name": "analyze_portfolio"},
    # Descriptions loaded when Claude calls tool
]
```

### Tool Execution with Circuit Breaker

```python
# In src/services/claude_agent/tool_executor.py
class ToolExecutor:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout_seconds=300
        )
        self.rate_limiter = RateLimiter({
            "execute_trade": 5,  # 5 trades/min
            "close_position": 10,
            "check_balance": 20
        })

    async def execute_tool(self, tool_name: str, params: dict) -> dict:
        # Rate limit check
        await self.rate_limiter.acquire(tool_name)

        # Circuit breaker check
        if self.circuit_breaker.is_open():
            raise CircuitBreakerOpenError()

        try:
            result = await self._execute(tool_name, params)
            self.circuit_breaker.record_success()
            return result
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise
```

## Session Flow

### Morning Prep Session

**Trigger**: `MARKET_OPEN` event (9:15 AM IST)

```python
# In ClaudeAgentService.run_morning_prep()
async def run_morning_prep_session(self, account_type: str = "paper"):
    # 1. Build context
    context = await self._build_morning_context(account_type)
    # {
    #     "balance": 100000.0,
    #     "buying_power": 80000.0,
    #     "open_positions": [...],
    #     "market_news": [...],
    #     "earnings_today": [...],
    #     "learnings": [...]  # From previous sessions
    # }

    # 2. Call SDK coordinator
    session_result = await self.claude_coordinator.run_morning_prep_session(
        account_type=account_type,
        context=context
    )

    # 3. Save session
    await self.claude_strategy_store.save_session(session_result)

    # 4. Publish event
    await self.event_bus.publish_async("AI_RECOMMENDATION", {
        "session_id": session_result.session_id,
        "recommendations": session_result.decisions_made
    })
```

### Evening Review Session

**Trigger**: `MARKET_CLOSE` event (3:30 PM IST)

```python
# In ClaudeAgentService.run_evening_review()
async def run_evening_review_session(self, account_type: str = "paper"):
    # 1. Build context
    context = await self._build_evening_context(account_type)
    # {
    #     "today_trades": [...],
    #     "pnl_today": 2500.0,
    #     "open_positions": [...],
    #     "market_summary": "NIFTY +0.5%, Bank NIFTY +1.2%"
    # }

    # 2. Call SDK coordinator
    session_result = await self.claude_coordinator.run_evening_review_session(
        account_type=account_type,
        context=context
    )

    # 3. Extract learnings
    learnings = session_result.learnings_extracted
    await self.claude_strategy_store.save_learnings(learnings)

    # 4. Publish event
    await self.event_bus.publish_async("EVENING_REVIEW_COMPLETE", {
        "session_id": session_result.session_id,
        "pnl_today": context["pnl_today"],
        "learnings": learnings
    })
```

## Token Budget Management

### Daily Token Limits

```python
# In ClaudeAgentService
DAILY_TOKEN_LIMITS = {
    "paper": 15000,  # 15K tokens/day for paper trading
    "live": 25000    # 25K tokens/day for live trading
}

async def check_token_budget(self, account_type: str) -> bool:
    """Check if daily token budget available"""
    usage_today = await self.claude_token_tracker.get_usage_today(account_type)
    limit = DAILY_TOKEN_LIMITS[account_type]

    if usage_today >= limit:
        logger.warning(f"Token limit reached: {usage_today}/{limit}")
        return False

    return True
```

### Token Tracking

```python
# After each session
await self.claude_token_tracker.record_usage(
    account_type=account_type,
    session_id=session_result.session_id,
    tokens_used=session_result.tokens_consumed,
    timestamp=datetime.utcnow()
)
```

## Coordinator Implementation Pattern

### Fixing Empty Coordinator Methods

**Current Problem** (`ClaudePaperTradingCoordinator`):

```python
# ❌ Returns empty results
async def generate_daily_strategy(self) -> dict:
    return {
        "recommended_trades": [],  # Empty!
        "market_analysis": "",
        "strategy_notes": ""
    }
```

**Solution**:

```python
# ✓ Actually calls Claude SDK
async def generate_daily_strategy(self) -> dict:
    # Get context
    account = await self.state.get_account(self.account_id)
    positions = await self.state.get_open_positions(self.account_id)
    market_data = await self.market_data_service.get_today_context()

    # Call Claude via SDK coordinator
    strategy_result = await self.claude_agent_service.run_morning_prep_session(
        account_type="paper"
    )

    # Parse recommendations
    recommended_trades = self._parse_trade_recommendations(
        strategy_result.decisions_made
    )

    return {
        "recommended_trades": recommended_trades,
        "market_analysis": strategy_result.market_context,
        "strategy_notes": strategy_result.notes
    }

def _parse_trade_recommendations(self, decisions: List[dict]) -> List[dict]:
    """Extract trade structure from Claude decisions"""
    trades = []
    for decision in decisions:
        if decision.get("type") == "TRADE":
            trades.append({
                "symbol": decision["symbol"],
                "action": decision["action"],
                "quantity": decision["quantity"],
                "entry_price": decision["price"],
                "stop_loss": decision.get("stop_loss"),
                "target": decision.get("target"),
                "strategy": decision.get("strategy", "ai_generated"),
                "reasoning": decision.get("reasoning", "")
            })
    return trades
```

## Learning Extraction

### Evening → Morning Context Loop

```python
# In EveningSessionCoordinator
async def _extract_learnings(self, session_result: ClaudeSessionResult) -> List[dict]:
    """Extract learnings from evening review for tomorrow's context"""
    learnings = []

    # Parse Claude's evaluation
    if "learned" in session_result.notes.lower():
        learnings.append({
            "type": "strategy_adjustment",
            "content": session_result.notes,
            "date": datetime.utcnow().date(),
            "relevance_score": 0.9
        })

    # Analyze today's trades
    for trade in session_result.trades_today:
        if trade["pnl"] < -1000:  # Significant loss
            learnings.append({
                "type": "risk_lesson",
                "content": f"Lost ₹{abs(trade['pnl'])} on {trade['symbol']} - avoid similar setups",
                "date": datetime.utcnow().date(),
                "relevance_score": 0.8
            })

    return learnings

# In MorningSessionCoordinator
async def _build_context_with_learnings(self, account_type: str) -> dict:
    """Include recent learnings in morning context"""
    recent_learnings = await self.claude_strategy_store.get_recent_learnings(
        account_type=account_type,
        days=7
    )

    return {
        ...
        "learnings": [
            learning["content"] for learning in recent_learnings
        ]
    }
```

## Error Handling

### SDK Client Errors

```python
try:
    session_result = await self.claude_coordinator.run_morning_prep_session(...)
except SDKAuthError:
    logger.error("Claude SDK authentication failed")
    # Use fallback strategy
except SDKTimeoutError:
    logger.error("Claude SDK timeout")
    # Retry with shorter timeout
except SDKTokenLimitError:
    logger.error("Token limit exceeded")
    # Skip session, alert user
```

## Best Practices

1. **Always load skills** - Include archived skills in system prompts
2. **Create agent profiles** - Define in `.claude/agents/` for discovery
3. **Use MCP tools** - Don't bypass tool executor
4. **Track tokens** - Monitor daily usage
5. **Extract learnings** - Evening → morning context loop
6. **Validate tool results** - Check tool response structure
7. **Handle SDK errors** - Fallback strategies when SDK unavailable
8. **Test with mock SDK** - Unit test coordinators without live SDK calls

## Integration Checklist

- [ ] Create agent profiles in `.claude/agents/`
- [ ] Integrate archived skills into prompts
- [ ] Fix coordinator methods (call SDK, not return empty)
- [ ] Wire MCP tools to backend services
- [ ] Implement learning extraction
- [ ] Add token tracking per session
- [ ] Test morning/evening session flow
- [ ] Handle SDK errors gracefully
- [ ] Document agent capabilities
- [ ] Update CLAUDE.md files
