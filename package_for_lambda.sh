#!/bin/bash

# Script to package the AI Internship Application Bot for AWS Lambda deployment

echo "📦 Packaging AI Internship Application Bot for AWS Lambda..."

# Create a temporary directory for packaging
echo "🗂️  Creating package directory..."
mkdir -p ./package

# Install dependencies to the package directory
echo "📚 Installing dependencies..."
pip install -r requirements.txt -t ./package

# Copy source code and configuration files
echo "📋 Copying source files..."
cp -r src/ ./package/
cp *.py ./package/
cp .env ./package/  # Copy environment variables

# Copy resume file if it exists
if [ -f "YARRAGOLLAHARIPRASAD Resume.pdf" ]; then
    echo "📄 Copying resume file..."
    cp "YARRAGOLLAHARIPRASAD Resume.pdf" ./package/
else
    echo "⚠️  Warning: Resume file not found. Make sure to include your resume in the Lambda package."
fi

# Create the zip file
echo "🗜️  Creating deployment zip file..."
cd package
zip -r ../deployment.zip .
cd ..

# Clean up
echo "🧹 Cleaning up..."
rm -rf ./package

echo "✅ Packaging complete! Your deployment.zip file is ready for AWS Lambda."
echo "📏 Zip file size: $(du -h deployment.zip | cut -f1)"

echo ""
echo "🚀 Next steps:"
echo "1. Upload deployment.zip to AWS Lambda"
echo "2. Set the handler to 'lambda_handler.handler'"
echo "3. Configure environment variables in the Lambda console"
echo "4. Set up an EventBridge rule to trigger the Lambda function every 3 hours"
echo ""