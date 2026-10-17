PRICING_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pricing — Card Scout</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <nav>
    <a href="/" class="logo">Card Scout</a>
    <div class="nav-links">
      <a href="/deals">Top Deals</a>
      <a href="/trending">📈 Trending</a>
      <a href="/tracked">📊 Tracked</a>
      <a href="/pricing">Pricing</a>
      <a href="/" class="cta">Home</a>
    </div>
  </nav>
</header>

<main>
  <section class="page-header">
    <h1>Simple, transparent pricing</h1>
    <p class="page-sub">2 live tiers + Pro coming soon. Cancel anytime. 14-day free trial.</p>
  </section>

  <section class="tiers">
    <div class="tier">
      <h3>Casual</h3>
      <p class="price">${{ casual_price }}<span>/month</span></p>
      <ul>
        <li>{{ casual_cards }} cards</li>
        <li>Discord alerts</li>
        <li>Self-serve dashboard</li>
      </ul>
      <p class="tier-best">Best for hobbyists starting out</p>
    </div>

    <div class="tier tier-popular">
      <span class="popular-badge">Most Popular</span>
      <h3>Deal-Pro</h3>
      <p class="price">${{ dealpro_price }}<span>/month</span></p>
      <ul>
        <li>{{ dealpro_cards }} cards</li>
        <li>Discord alerts</li>
        <li>All features unlocked</li>
      </ul>
      <p class="tier-best">Best for active collectors and dealers</p>
    </div>

    <div class="tier tier-coming-soon">
      <span class="coming-soon-badge">Coming Soon</span>
      <h3>Pro</h3>
      <p class="price">${{ pro_price }}<span>/month</span></p>
      <ul>
        <li>150 cards</li>
        <li>Discord alerts</li>
        <li>Custom thresholds</li>
        <li class="coming-soon-feature">Population context (PSA/BGS/SGC/CGC)</li>
        <li class="coming-soon-feature">Player-level trend aggregation</li>
        <li class="coming-soon-feature">Cert # lookup &amp; vault tracking</li>
      </ul>
      <p class="tier-best">Best for dealers with daily volume — population data launches as we hit subscriber scale</p>
    </div>

    <div class="tier">
      <h3>Enterprise</h3>
      <p class="price">Contact Us</p>
      <ul>
        <li>Unlimited cards</li>
        <li>Full stream access</li>
        <li>Custom integrations</li>
      </ul>
      <p class="tier-best">For institutional volume</p>
      <a href="mailto:support@cardscout.pro" class="btn btn-secondary" style="display:block; text-align:center; margin-top:16px;">Contact us</a>
    </div>
  </section>
</main>
<footer>
  <p>&copy; 2026 Card Scout. <a href="/">Home</a> · <a href="/deals">Top Deals</a></p>
</footer>
</body>
</html>
'''