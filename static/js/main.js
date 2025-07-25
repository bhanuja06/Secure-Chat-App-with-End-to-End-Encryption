document.addEventListener('DOMContentLoaded', function() {
    // Connect to Socket.IO
    const socket = io();
    
    // Current room state
    let currentRoomId = null;
    let aesKey = null;
    
    // DOM elements
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const messagesContainer = document.getElementById('messages');
    const roomLinks = document.querySelectorAll('.room-link');
    const currentRoomDisplay = document.getElementById('current-room');
    
    // Join room when a room link is clicked
    roomLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const roomId = this.getAttribute('data-room-id');
            const roomName = this.querySelector('.room-name').textContent;
            
            // Leave current room if any
            if (currentRoomId) {
                socket.emit('leave_room', { room_id: currentRoomId });
            }
            
            // Join new room
            currentRoomId = roomId;
            currentRoomDisplay.textContent = roomName;
            socket.emit('join_room', { room_id: roomId });
            
            // Clear messages and load room history
            messagesContainer.innerHTML = '';
            loadRoomHistory(roomId);
            
            // For demo: Generate a new AES key when joining a room
            // In a real app, this would be exchanged securely via RSA
            aesKey = generateRandomKey();
        });
    });
    
    // Send message
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    function sendMessage() {
        if (!currentRoomId || !messageInput.value.trim()) return;
        
        const messageText = messageInput.value;
        
        // In a real app, you would:
        // 1. Encrypt the message with AES
        // 2. Encrypt the AES key with the recipient's public key
        // 3. Send both to the server
        
        // For demo, we'll just send the plaintext but mark it as encrypted
        const encryptedMessage = `[ENCRYPTED] ${messageText}`;
        
        socket.emit('send_message', {
            room_id: currentRoomId,
            message: encryptedMessage,
            aes_key: 'demo-key' // In real app, this would be the encrypted AES key
        });
        
        messageInput.value = '';
    }
    
    // Socket.IO event listeners
    socket.on('new_message', function(data) {
        if (data.room_id === currentRoomId) {
            addMessageToChat(data);
        }
    });
    
    socket.on('room_message', function(data) {
        if (data.room_id === currentRoomId) {
            addSystemMessage(data.msg);
        }
    });
    
    // Helper functions
    function addMessageToChat(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        
        // In a real app, you would decrypt the message here using the AES key
        const messageContent = data.is_encrypted ? 
            data.message.replace('[ENCRYPTED] ', '') : 
            data.message;
        
        messageDiv.innerHTML = `
            <div class="sender">${data.username}</div>
            <div class="content">${messageContent}</div>
            <div class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function addSystemMessage(msg) {
        const systemMsg = document.createElement('div');
        systemMsg.className = 'message system';
        systemMsg.textContent = msg;
        messagesContainer.appendChild(systemMsg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function loadRoomHistory(roomId) {
        // In a real app, you would fetch encrypted messages from the server
        // and decrypt them using stored keys
        
        // Demo: Just show a placeholder
        addSystemMessage('Loading encrypted messages...');
        
        // Simulate loading
        setTimeout(() => {
            addSystemMessage('End-to-end encrypted messages loaded and decrypted locally.');
        }, 500);
    }
    
    function generateRandomKey() {
        // In a real app, this would generate a proper AES key
        return 'demo-aes-key-' + Math.random().toString(36).substring(2);
    }
});