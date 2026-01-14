document.addEventListener('DOMContentLoaded', () => {
  const updateCryptoPrices = () => {
    const cards = document.querySelectorAll('.crypto-card');
    const symbols = Array.from(cards).map(el => el.getAttribute('data-symbol')).filter(Boolean);

    if (symbols.length === 0) return;

    const ids = [...new Set(symbols)].join(',');

    fetch(`https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=usd`)
      .then(res => res.json())
      .then(data => {
        cards.forEach(el => {
          const symbol = el.getAttribute('data-symbol');
          const icon = el.getAttribute('data-icon') || 'chip'; // fallback icon
          const price = data[symbol]?.usd?.toLocaleString() ?? 'N/A';

          el.innerHTML = `
            <div class="card" style="text-align: center; text-decoration: none;">
              <div class="card-content">
                <h3 class="card-title">${symbol.toUpperCase()}</h3>
                <p class="card-subtitle">USD: $${price}</p>
              </div>
            </div>`;
        });
      })
      .catch(error => {
        console.error('Error fetching crypto prices:', error);
      });
  };

  updateCryptoPrices();
  setInterval(updateCryptoPrices, 10000);
});
