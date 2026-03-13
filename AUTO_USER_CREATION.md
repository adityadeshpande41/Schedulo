# Auto User Creation from Google Calendar

## What Changed

The system now automatically creates a new user when someone connects their Google Calendar for the first time!

## How It Works

### 1. User Clicks "Connect Google Calendar"
- System initiates OAuth with `user_id=new`
- User is redirected to Google for authentication

### 2. Google OAuth Flow
- User authenticates with their Google account
- Google returns:
  - Access token (for calendar access)
  - Refresh token (for long-term access)
  - User info (email, name, profile picture)

### 3. Auto User Creation
- Backend receives OAuth callback
- If `user_id=new`, creates a new user:
  ```python
  new_user = User(
      id="u_abc12345",  # Generated UUID
      name="John Doe",   # From Google
      email="john@gmail.com",  # From Google
      role="User",
      timezone="America/New_York"
  )
  ```

### 4. Calendar Integration Saved
- Saves calendar tokens for the new user
- User can now access their Google Calendar events

### 5. Dashboard Auto-Switch
- Redirects to: `/dashboard?user_id=u_abc12345`
- Dashboard automatically switches to show the new user
- User sees their own calendar!

## User Experience

### Before (Old Behavior)
1. Open Schedulo → Shows Alex Rivera's calendar (hardcoded)
2. Connect your Google Calendar → Still shows Alex's calendar
3. Confusing! 😕

### After (New Behavior)
1. Open Schedulo → Shows default demo user
2. Click "Connect Google Calendar"
3. Authenticate with your Google account
4. **Automatically creates your user account**
5. **Dashboard switches to show YOUR calendar** ✨
6. You see your own meetings and events!

## Technical Details

### Files Modified

**Backend:**
- `python_backend/integrations/google_calendar.py`
  - Added user info fetching from Google OAuth
  - Added scopes: `userinfo.email`, `userinfo.profile`

- `python_backend/api/routes/calendar.py`
  - Auto-creates user if `user_id=new`
  - Returns `user_id` in redirect URL

**Frontend:**
- `client/src/components/schedulo/calendar-connect.tsx`
  - Changed to use `user_id=new` for new connections

- `client/src/pages/dashboard.tsx`
  - Added URL param detection for `user_id`
  - Auto-switches to new user after OAuth

### Database Schema

New users are created with:
```sql
INSERT INTO users (id, name, email, role, timezone)
VALUES ('u_abc12345', 'John Doe', 'john@gmail.com', 'User', 'America/New_York');
```

Calendar integration is linked:
```sql
INSERT INTO calendar_integrations (user_id, provider, access_token, refresh_token)
VALUES ('u_abc12345', 'google', '...', '...');
```

## Demo Mode Features

### User Switcher
- Dropdown in top-right of dashboard
- Switch between different users
- Useful for testing multi-agent coordination

### Multiple Calendars
- Connect different Google accounts
- Each creates a new user
- Test scheduling between real calendars!

## Testing

### Test Scenario 1: New User
1. Open fresh browser/incognito
2. Go to dashboard
3. Click "Connect Google Calendar"
4. Authenticate with your Google account
5. ✅ Should see your calendar events

### Test Scenario 2: Multiple Users
1. Connect first Google account → Creates User A
2. Use user switcher to go back to demo user
3. Connect second Google account → Creates User B
4. Switch between users to see different calendars

### Test Scenario 3: Multi-Agent Scheduling
1. Connect 2-3 different Google accounts
2. Each becomes a user in Schedulo
3. Schedule a meeting with multiple attendees
4. AI agents coordinate across real calendars!

## Benefits

### For Users
- ✅ No manual account creation
- ✅ Instant access to their calendar
- ✅ Seamless onboarding experience

### For Demos
- ✅ Show real calendar integration
- ✅ Test with actual Google Calendar data
- ✅ Demonstrate multi-agent coordination with real users

### For Development
- ✅ Easy testing with multiple accounts
- ✅ No need to seed fake users
- ✅ Real-world data for AI training

## Privacy & Security

### What's Stored
- ✅ User email (from Google)
- ✅ User name (from Google)
- ✅ Calendar access tokens (encrypted)
- ✅ Calendar events (cached locally)

### What's NOT Stored
- ❌ Google password
- ❌ Full Google account access
- ❌ Other Google services data

### Token Security
- Tokens stored in database
- Refresh tokens for long-term access
- Tokens can be revoked by disconnecting calendar

## Future Enhancements

### Phase 1: Better Onboarding
- [ ] Welcome screen for new users
- [ ] Timezone detection from browser
- [ ] Profile picture from Google

### Phase 2: User Management
- [ ] Edit profile (name, timezone, preferences)
- [ ] Delete account
- [ ] Export data

### Phase 3: Multi-Calendar
- [ ] Connect multiple calendars per user
- [ ] Outlook/Microsoft 365 integration
- [ ] Apple Calendar integration

## Troubleshooting

### Issue: "User not found" error
**Solution**: Make sure backend is running and database is initialized

### Issue: OAuth fails with "access_denied"
**Solution**: Add your email to test users in Google Cloud Console

### Issue: Dashboard shows wrong user
**Solution**: Use the user switcher dropdown to select correct user

### Issue: Calendar events not showing
**Solution**: Click "Sync Calendar" or wait for automatic sync

## Summary

The system now provides a seamless experience where connecting a Google Calendar automatically creates a user account and shows that user's calendar. This makes demos more impressive and testing more realistic!

**Key Improvement**: From "hardcoded demo user" to "dynamic user creation from real Google accounts" 🚀
