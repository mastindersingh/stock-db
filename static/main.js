function loadStockRecommendations() {
    fetch('/api/stock-recommendations')  // Replace with your API endpoint
        .then(response => response.json())
        .then(recommendations => {
            const recommendationsSection = document.getElementById('stock-recommendations');
            recommendations.forEach(stock => {
                const div = document.createElement('div');
                div.innerHTML = `
                    <h3>${stock.name}</h3>
                    <p>Price: ${stock.price}</p>
                    <p>Recommendation: ${stock.recommendation}</p>
                `;
                recommendationsSection.appendChild(div);
            });
        })
        .catch(error => console.error('Error:', error));
}

window.onload = function() {
    loadStockRecommendations();
};

