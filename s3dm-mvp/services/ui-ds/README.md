# UI/DS (User Interface & Designer Sandbox)

This directory is for the frontend application.

**For MVP, it currently serves a placeholder HTML page.**

## Next Steps for Frontend Development:

1.  **Initialize a React/Vue Project**:
    \`\`\`bash
    # Inside this directory (services/ui-ds)
    # For React:
    npx create-react-app .
    # For Vue:
    npm init vue@latest
    \`\`\`
2.  **Update Dockerfile**: Replace the Nginx Dockerfile with one that builds and serves your React/Vue app (e.g., using Node.js for development server, or building static assets for Nginx).
3.  **Update docker-compose.yml**: Adjust the \`command\` for the \`ui-ds\` service to run your frontend development server (e.g., \`npm start\`).