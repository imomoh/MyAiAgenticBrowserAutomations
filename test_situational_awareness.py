#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced situational awareness features
of the browser agent.
"""

import sys
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from agent.browser_agent import BrowserAgent
from loguru import logger

def test_situational_awareness():
    """Test the enhanced situational awareness features."""
    
    # Initialize the browser agent
    agent = BrowserAgent(keep_browser_open=True)
    
    try:
        # Start the agent
        agent.start()
        logger.info("🚀 Browser agent started")
        
        # Test 1: Navigate to a simple page and analyze situation
        logger.info("\n" + "="*50)
        logger.info("TEST 1: Basic situational analysis")
        logger.info("="*50)
        
        result = agent.execute_task("Navigate to https://example.com")
        if result.success:
            logger.info("✅ Navigation successful")
            
            # Get situational analysis
            situation = agent.get_current_situation_analysis("Get the page title")
            logger.info(f"📊 Page type: {situation.get('page_type', 'unknown')}")
            logger.info(f"📊 Recommended approach: {situation.get('recommended_approach', 'unknown')}")
            logger.info(f"📊 Confidence level: {situation.get('confidence_level', 0)}")
            logger.info(f"📊 Potential obstacles: {situation.get('potential_obstacles', [])}")
            logger.info(f"📊 Task intent: {situation.get('task_analysis', {}).get('intent', [])}")
        
        # Test 2: Test with a search page
        logger.info("\n" + "="*50)
        logger.info("TEST 2: Search page situational analysis")
        logger.info("="*50)
        
        result = agent.execute_task("Navigate to https://www.google.com")
        if result.success:
            logger.info("✅ Navigation to Google successful")
            
            # Get situational analysis for a search task
            situation = agent.get_current_situation_analysis("Search for 'browser automation'")
            logger.info(f"📊 Page type: {situation.get('page_type', 'unknown')}")
            logger.info(f"📊 Recommended approach: {situation.get('recommended_approach', 'unknown')}")
            logger.info(f"📊 Confidence level: {situation.get('confidence_level', 0)}")
            logger.info(f"📊 Potential obstacles: {situation.get('potential_obstacles', [])}")
            logger.info(f"📊 Task intent: {situation.get('task_analysis', {}).get('intent', [])}")
            logger.info(f"📊 Contextual relevance: {situation.get('contextual_relevance', {}).get('relevance_score', 0)}")
        
        # Test 3: Test complex task with situational awareness
        logger.info("\n" + "="*50)
        logger.info("TEST 3: Complex task with situational awareness")
        logger.info("="*50)
        
        result = agent.execute_task("Navigate to https://httpbin.org/forms/post and fill out the form")
        if result.success:
            logger.info("✅ Complex task execution successful")
            
            # Get situational analysis for the complex task
            situation = agent.get_current_situation_analysis("Fill out the form and submit it")
            logger.info(f"📊 Page type: {situation.get('page_type', 'unknown')}")
            logger.info(f"📊 Recommended approach: {situation.get('recommended_approach', 'unknown')}")
            logger.info(f"📊 Confidence level: {situation.get('confidence_level', 0)}")
            logger.info(f"📊 Potential obstacles: {situation.get('potential_obstacles', [])}")
            logger.info(f"📊 Success indicators: {situation.get('success_indicators', [])}")
            logger.info(f"📊 Task complexity: {situation.get('task_analysis', {}).get('complexity', 'unknown')}")
        
        # Test 4: Test error recovery with situational awareness
        logger.info("\n" + "="*50)
        logger.info("TEST 4: Error recovery with situational awareness")
        logger.info("="*50)
        
        result = agent.execute_task("Click on a non-existent button")
        if not result.success:
            logger.info("✅ Expected error occurred")
            logger.info(f"❌ Error: {result.error}")
            
            # Get situational analysis after error
            situation = agent.get_current_situation_analysis("Find and click a button")
            logger.info(f"📊 Page type: {situation.get('page_type', 'unknown')}")
            logger.info(f"📊 Recommended approach: {situation.get('recommended_approach', 'unknown')}")
            logger.info(f"📊 Potential obstacles: {situation.get('potential_obstacles', [])}")
        
        logger.info("\n" + "="*50)
        logger.info("✅ All situational awareness tests completed!")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    
    finally:
        # Keep browser open for manual inspection
        logger.info("🔄 Browser kept open for manual inspection. Close it manually when done.")
        # agent.stop()  # Uncomment to close browser automatically

if __name__ == "__main__":
    test_situational_awareness() 