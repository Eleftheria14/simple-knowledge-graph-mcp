#!/bin/bash

# GitHub Repository Setup Commands
# Run these after creating your repository on GitHub.com

echo "🚀 Setting up GitHub repository..."

# Replace 'yourusername' with your actual GitHub username
read -p "Enter your GitHub username: " USERNAME

# Add remote origin
git remote add origin https://github.com/$USERNAME/scientific-paper-analyzer.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main

echo "✅ Repository successfully pushed to GitHub!"
echo "🌐 Your repository is now available at:"
echo "   https://github.com/$USERNAME/scientific-paper-analyzer"