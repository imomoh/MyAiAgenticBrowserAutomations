#!/usr/bin/env python3
"""
Test script to verify improved element finding and clicking functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.browser_agent import BrowserAgent
from loguru import logger
import time

def test_element_finding():
    """Test the improved element finding capabilities."""
    
    # Create browser agent
    agent = BrowserAgent(keep_browser_open=True, manual_interaction=True)
    
    try:
        # Start the browser
        agent.start()
        logger.info("🚀 Browser started successfully")
        
        # Navigate to a test page
        test_url = "https://example.com"
        logger.info(f"🌐 Navigating to {test_url}")
        agent.execute_task(f"Navigate to {test_url}")
        
        # Wait a moment for page to load
        time.sleep(2)
        
        # Test listing available elements
        logger.info("📋 Listing available elements...")
        elements_info = agent.list_available_elements()
        logger.info(f"Found {elements_info.get('total_elements', 0)} interactive elements")
        
        # Print some example elements
        for elem in elements_info.get('elements', [])[:5]:
            logger.info(f"  - {elem.get('tag', '')} '{elem.get('text', '')}' (selector: {elem.get('best_selector', '')})")
        
        # Test clicking on a link (More information link on example.com)
        logger.info("🖱️ Testing click on 'More information' link...")
        result = agent.execute_task("Click on the More information link")
        
        if result.success:
            logger.info("✅ Click test successful!")
        else:
            logger.error(f"❌ Click test failed: {result.error}")
            
            # Try debugging
            logger.info("🔍 Debugging element selection...")
            debug_info = agent.debug_element_selection("Click on More information link")
            logger.info(f"Debug found {len(debug_info.get('available_elements', []))} elements")
        
        # Keep browser open for manual inspection
        logger.info("🔍 Browser kept open for manual inspection. Press Enter to continue...")
        input()
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    finally:
        # Stop the agent
        agent.stop()
        logger.info("🛑 Test completed")

if __name__ == "__main__":
    test_element_finding() 