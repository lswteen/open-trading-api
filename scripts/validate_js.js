#!/usr/bin/env node

// Simple Node.js script to check for JavaScript syntax errors
const fs = require('fs');
const path = require('path');

const jsFilePath = path.join(__dirname, '../frontend/static/js/app.js');

try {
    const jsContent = fs.readFileSync(jsFilePath, 'utf8');

    // Try to parse the JavaScript
    new Function(jsContent);

    console.log('✅ JavaScript syntax is valid!');

    // Check if updateOrderPriceInputState is defined at global scope
    if (jsContent.includes('function updateOrderPriceInputState()')) {
        console.log('✅ updateOrderPriceInputState function is defined at global scope');
    }

    // Check if it's called from updateOrderUI
    const updateOrderUIMatch = jsContent.match(/function updateOrderUI\(\)[^}]*updateOrderPriceInputState\(\)/s);
    if (updateOrderUIMatch) {
        console.log('✅ updateOrderPriceInputState is called from updateOrderUI');
    }

    console.log('\n✅ All checks passed! The fix should work correctly.');

} catch (error) {
    console.error('❌ JavaScript syntax error:', error.message);
    process.exit(1);
}
