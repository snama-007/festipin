#!/bin/bash

echo "🧪 Testing Party Summary UI Components..."
echo "========================================"

# Check if frontend server is running
echo "📡 Checking frontend server..."
if curl -s http://localhost:3001 > /dev/null; then
    echo "✅ Frontend server is running on port 3001"
else
    echo "❌ Frontend server not running. Starting..."
    cd /Users/snama/s.space/Parx-Agentic-Verse/festipin/frontend
    npm run dev -- -p 3001 &
    sleep 5
fi

echo ""
echo "🎯 Test URLs:"
echo "============="
echo "1. Main Test Page: http://localhost:3001/test-party-summary"
echo "2. Dev Page (with integration): http://localhost:3001/dev"
echo ""

echo "📋 Test Steps:"
echo "=============="
echo "1. Open http://localhost:3001/test-party-summary in your browser"
echo "2. Click 'Test Party Summary UI' button"
echo "3. Verify the following components load:"
echo "   ✅ Party Summary header with completion percentage"
echo "   ✅ Budget visualization with progress bar"
echo "   ✅ Plan cards for theme, venue, cake, catering, vendors"
echo "   ✅ Recommendations list"
echo "   ✅ Next button to communication hub"
echo ""

echo "🔍 What to Look For:"
echo "==================="
echo "✅ Smooth animations and transitions"
echo "✅ Responsive design (try different screen sizes)"
echo "✅ Demo data loads correctly"
echo "✅ All components render without errors"
echo "✅ Navigation between views works"
echo ""

echo "🐛 If you see errors:"
echo "===================="
echo "1. Check browser console for JavaScript errors"
echo "2. Verify all components are imported correctly"
echo "3. Check that demo data is loading"
echo "4. Ensure Tailwind CSS is working"
echo ""

echo "🎉 Happy Testing!"
