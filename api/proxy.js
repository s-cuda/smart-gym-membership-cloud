const fetch = require('node-fetch');

module.exports = async function (context, req) {
    // Your VM backend URL
    const VM_BACKEND = 'http://172.176.96.72:8000';
    
    // Get the path after /api/
    const path = context.bindingData.restOfPath || '';
    
    // Build full URL
    const url = `${VM_BACKEND}/${path}`;
    
    // Get query string if present
    const queryString = req.url.includes('?') ? req.url.split('?')[1] : '';
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    
    context.log(`Proxying ${req.method} request to: ${fullUrl}`);
    
    try {
        const options = {
            method: req.method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        // Add body for POST/PUT/PATCH requests
        if (req.body && ['POST', 'PUT', 'PATCH'].includes(req.method)) {
            options.body = JSON.stringify(req.body);
        }
        
        const response = await fetch(fullUrl, options);
        const contentType = response.headers.get('content-type');
        
        let data;
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }
        
        context.res = {
            status: response.status,
            body: data,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        };
        
    } catch (error) {
        context.log.error('Proxy error:', error);
        context.res = {
            status: 500,
            body: { 
                error: 'Backend connection failed',
                message: error.message,
                backend: VM_BACKEND
            },
            headers: {
                'Content-Type': 'application/json'
            }
        };
    }
};