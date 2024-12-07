# Use official Node.js image as the base
FROM node:16-slim

# Set working directory
WORKDIR /usr/src/app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app's code
COPY . .

# Expose the default React development server port
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]