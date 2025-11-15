# 🔧 Voice Tutor Connection Troubleshooting Guide

## 🚨 **"Failed to connect to Kashar AI" Error**

If you're seeing this error when clicking "Start Live Session", follow these steps:

---

## 📋 **Step-by-Step Troubleshooting**

### **1. Check Authentication Status**
- ✅ **Make sure you're logged in** to the application
- ✅ **Refresh the page** and log in again if needed
- ✅ **Check browser console** for "Auth token check" message

**How to check:**
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Click "Start Live Session"
4. Look for: `Auth token check: Token found` or `No token found`

### **2. Grant Microphone Permissions**
- ✅ **Allow microphone access** when prompted
- ✅ **Check browser permissions** in address bar
- ✅ **Reset permissions** if blocked

**How to fix:**
1. Click the 🔒 lock icon in browser address bar
2. Set Microphone to "Allow"
3. Refresh the page and try again

### **3. Check Browser Console for Errors**
- ✅ **Open Developer Tools** (F12)
- ✅ **Look for error messages** in Console tab
- ✅ **Check Network tab** for failed requests

**Common error messages:**
- `Authentication required` → Log in first
- `Network error` → Check internet connection
- `Agora initialization failed` → Microphone permissions issue

### **4. Network and CORS Issues**
- ✅ **Check if backend is running** on http://localhost:8000
- ✅ **Check if frontend is running** on http://localhost:3000
- ✅ **Verify API endpoints** are accessible

**Quick test:**
- Visit: http://localhost:8000/docs (should show API documentation)
- Visit: http://localhost:3000 (should show the app)

---

## 🔍 **Detailed Debugging Steps**

### **Check Browser Console Messages**

When you click "Start Live Session", you should see these messages in console:

```
✅ Good messages:
Auth token check: Token found
Starting voice session...
Session started successfully: {session_id: "...", ...}
Connected to Kashar AI!

❌ Error messages:
Auth token check: No token found
→ Solution: Log in first

Network error - please check your connection
→ Solution: Check if backend is running

Server error: 401/403
→ Solution: Log out and log in again
```

### **Check Network Tab**

1. Open Developer Tools → Network tab
2. Click "Start Live Session"
3. Look for the request to `/api/tutor/voice/start-session`

**Expected result:**
- ✅ Status: 200 OK
- ✅ Response contains: `session_id`, `agora_tokens`, `channel_name`

**Error results:**
- ❌ Status: 401 → Authentication issue
- ❌ Status: 403 → Permission issue
- ❌ Status: 500 → Server error
- ❌ No request → Frontend issue

---

## 🛠️ **Quick Fixes**

### **Fix 1: Authentication Issues**
```bash
# Clear browser storage and log in again
1. Open Developer Tools (F12)
2. Go to Application tab
3. Clear Local Storage
4. Refresh page and log in again
```

### **Fix 2: Microphone Permissions**
```bash
# Reset browser permissions
1. Go to browser Settings
2. Search for "Site permissions"
3. Find localhost:3000
4. Reset microphone permissions
5. Refresh and try again
```

### **Fix 3: Backend Connection**
```bash
# Restart backend service
cd /Users/tusharjoshi/Desktop/Hackfest\ 2025/Kashar\ AI/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **Fix 4: Frontend Issues**
```bash
# Restart frontend
cd /Users/tusharjoshi/Desktop/Hackfest\ 2025/Kashar\ AI/frontend
npm start
```

---

## 🎯 **Expected Behavior**

### **Successful Connection Flow:**
1. Click "Start Live Session"
2. Browser asks for microphone permission → **Click Allow**
3. See "Connecting..." message
4. See "Connected to Kashar AI!" success message
5. Welcome message appears from Kashar
6. Voice controls become active

### **What Should Work:**
- ✅ **Text chat** with Kashar AI
- ✅ **Voice recording** (push-to-talk)
- ✅ **Audio playback** of AI responses
- ✅ **Session management** (connect/disconnect)

---

## 📞 **Still Having Issues?**

### **Check These Common Problems:**

1. **Browser Compatibility**
   - Use Chrome, Firefox, or Safari
   - Ensure browser is up to date
   - Disable ad blockers temporarily

2. **System Permissions**
   - Check system microphone permissions
   - Ensure no other apps are using microphone
   - Test microphone in other applications

3. **Network Issues**
   - Check firewall settings
   - Ensure ports 3000 and 8000 are accessible
   - Try disabling VPN temporarily

### **Debug Information to Collect:**
- Browser console error messages
- Network tab request/response details
- Browser and OS version
- Microphone permissions status

---

## ✅ **Verification Steps**

After fixing issues, verify everything works:

1. ✅ **Login successful** - can access dashboard
2. ✅ **Navigate to Live Tutor** - page loads correctly
3. ✅ **Click Start Live Session** - no error messages
4. ✅ **Microphone permission** - granted successfully
5. ✅ **Connection established** - success message appears
6. ✅ **Welcome message** - Kashar greets you
7. ✅ **Voice controls** - mute/unmute buttons work
8. ✅ **Text chat** - can send messages to Kashar

---

**🎤 Once everything is working, you'll be able to have natural voice conversations with Kashar AI using ElevenLabs for high-quality speech recognition and synthesis!**
