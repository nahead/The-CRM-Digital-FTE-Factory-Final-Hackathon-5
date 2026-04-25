# ProjectFlow - Product Documentation

## Getting Started

### Account Setup
1. **Sign Up:** Visit projectflow.techcorp.com/signup
2. **Verify Email:** Check your inbox for verification link
3. **Create Workspace:** Choose a workspace name (can be changed later)
4. **Invite Team:** Add team members via email

### Creating Your First Project
1. Click "New Project" in the dashboard
2. Enter project name and description
3. Choose project template (Kanban, Scrum, Custom)
4. Set project visibility (Public/Private)
5. Add team members to the project

## Core Features

### Task Management
- **Create Task:** Click "+" button or press 'N' key
- **Assign Task:** Click on task → Assign to team member
- **Set Due Date:** Click calendar icon in task details
- **Add Labels:** Use labels for categorization (bug, feature, urgent, etc.)
- **Task Status:** Drag tasks between columns (To Do, In Progress, Done)
- **Subtasks:** Break down complex tasks into smaller steps

### Collaboration
- **Comments:** Add comments to tasks with @mentions
- **File Attachments:** Drag and drop files (max 50MB per file)
- **Real-time Updates:** See changes instantly across all devices
- **Activity Feed:** Track all project activities in one place

### Time Tracking
- **Start Timer:** Click timer icon on any task
- **Manual Entry:** Add time manually if you forgot to track
- **Reports:** View time reports by project, user, or date range
- **Export:** Download time reports as CSV or PDF

### Integrations

#### Slack Integration
1. Go to Settings → Integrations
2. Click "Connect Slack"
3. Authorize ProjectFlow in Slack
4. Choose which notifications to receive
5. Use `/projectflow` command in Slack

#### GitHub Integration
1. Go to Settings → Integrations
2. Click "Connect GitHub"
3. Authorize ProjectFlow to access repositories
4. Link commits to tasks using #TASK-ID in commit messages
5. Auto-close tasks when PR is merged

#### Google Workspace
1. Settings → Integrations → Google Workspace
2. Sign in with Google account
3. Sync calendar events with project deadlines
4. Import contacts for easy team invitations

### Mobile Apps
- **iOS:** Download from App Store (iOS 14+)
- **Android:** Download from Google Play (Android 8+)
- **Features:** Full task management, offline mode, push notifications
- **Sync:** Automatic sync when online

### API Access
- **API Key:** Generate in Settings → API
- **Documentation:** api.techcorp.com/docs
- **Rate Limits:** 1000 requests/hour (Starter), 10,000/hour (Pro), Unlimited (Enterprise)
- **Webhooks:** Configure webhooks for real-time updates

## Common Tasks

### How to Reset Password
1. Go to login page
2. Click "Forgot Password"
3. Enter your email address
4. Check inbox for reset link (valid for 1 hour)
5. Create new password (min 8 characters)

### How to Change Workspace Name
1. Settings → Workspace Settings
2. Click "Edit" next to workspace name
3. Enter new name
4. Click "Save Changes"
Note: Only workspace admins can change this

### How to Export Project Data
1. Open project
2. Click "..." menu → Export
3. Choose format (CSV, JSON, PDF)
4. Select date range
5. Click "Download"

### How to Manage Permissions
**Project Level:**
- Admin: Full control
- Member: Can create/edit tasks
- Viewer: Read-only access

**Workspace Level:**
- Owner: Full control, billing access
- Admin: Manage users and projects
- Member: Access assigned projects only

### How to Upgrade/Downgrade Plan
1. Settings → Billing
2. Click "Change Plan"
3. Select new plan
4. Confirm changes
5. Billing adjusts pro-rata

## Troubleshooting

### Mobile App Not Syncing
- Check internet connection
- Force close and reopen app
- Log out and log back in
- Clear app cache (Settings → Storage)
- Reinstall app if issue persists

### Slack Notifications Not Working
- Verify integration is connected (Settings → Integrations)
- Check Slack notification preferences
- Ensure ProjectFlow bot is added to relevant channels
- Reconnect integration if needed

### Can't Upload Files
- Check file size (max 50MB)
- Verify file format is supported
- Check storage quota (Settings → Usage)
- Try different browser
- Disable browser extensions temporarily

### GitHub Commits Not Linking
- Verify GitHub integration is active
- Use correct format: #TASK-ID in commit message
- Check repository permissions
- Reconnect GitHub if needed

## Limitations
- **File Storage:** 10GB (Starter), 100GB (Pro), 1TB (Enterprise)
- **Projects:** 10 (Starter), Unlimited (Pro/Enterprise)
- **Integrations:** 3 (Starter), Unlimited (Pro/Enterprise)
- **API Calls:** 1K/hour (Starter), 10K/hour (Pro), Unlimited (Enterprise)
- **Video Calls:** 30 min (Starter), 2 hours (Pro), Unlimited (Enterprise)

## Support Resources
- Knowledge Base: help.techcorp.com
- Video Tutorials: youtube.com/techcorp
- Community Forum: community.techcorp.com
- Status Page: status.techcorp.com
- Contact Support: support@techcorp.com
