console.log("Manani, Women's Pride script loaded!");

document.addEventListener('DOMContentLoaded', () => {
    // Dynamic Product Population
    const productGrid = document.querySelector('.product-grid');
    const products = [
        { id: 1, name: 'Elegant Dress', price: '79.99', image: 'https://via.placeholder.com/200x200?text=Dynamic+Product+1' },
        { id: 2, name: 'Stylish Top', price: '39.99', image: 'https://via.placeholder.com/200x200?text=Dynamic+Product+2' },
        { id: 3, name: 'Chic Skirt', price: '49.99', image: 'https://via.placeholder.com/200x200?text=Dynamic+Product+3' },
        { id: 4, name: 'Fashionable Bag', price: '89.99', image: 'https://via.placeholder.com/200x200?text=Dynamic+Product+4' },
        { id: 5, name: 'Trendy Jeans', price: '59.99', image: 'https://via.placeholder.com/200x200?text=Dynamic+Product+5' },
        { id: 6, name: 'Summer Sandals', price: '34.99', image: 'https://via.placeholder.com/200x200?text=Dynamic+Product+6' },
    ];

    // Clear existing placeholder products if any (from HTML)
    productGrid.innerHTML = '';

    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.classList.add('product-card');
        productCard.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
            <h4>${product.name}</h4>
            <p>$${product.price}</p>
            <button class="add-to-cart-btn" data-product-id="${product.id}" data-product-name="${product.name}">Add to Cart</button>
        `;
        productGrid.appendChild(productCard);
    });

    // Add to Cart Button Logic
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            const productName = event.target.dataset.productName;
            console.log(`Added "${productName}" to cart! (ID: ${event.target.dataset.productId})`);
            // In a real app, this would add to a cart object/database
            alert(`"${productName}" added to your cart!`);
        });
    });

    // Hero Section "Shop Now" Button Logic
    const shopNowBtn = document.querySelector('.hero-section .btn');
    if (shopNowBtn) {
        shopNowBtn.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent default anchor behavior
            console.log("Shop Now button clicked! Redirecting to products...");
            // In a real app, this would redirect to a products page
            alert("Redirecting to our amazing collection!");
        });
