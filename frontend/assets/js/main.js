const API_BASE_URL = `http://${window.location.hostname}:5000/api`;
const SOCKET_BASE_URL = `http://${window.location.hostname}:5000`;

// --- Live Sign Language Demo Integration ---
let jwtToken = localStorage.getItem('access_token'); // Assume token is stored after login

function startLiveDemo() {
  const socket = io(SOCKET_BASE_URL); // Use dynamic backend IP
  const video = document.createElement('video');
  video.autoplay = true;
  video.width = 320;
  video.height = 240;
  video.setAttribute('aria-label', 'Live Sign Language Camera');
  document.getElementById('video-to-text').appendChild(video);

  const loader = document.createElement('div');
  loader.id = 'loader';
  loader.innerHTML = '<span>Loading model...</span>';
  loader.style.textAlign = 'center';
  loader.style.fontSize = '1.2em';
  document.getElementById('video-to-text').appendChild(loader);

  navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
    video.srcObject = stream;
    const canvas = document.createElement('canvas');
    canvas.width = video.width;
    canvas.height = video.height;
    loader.innerHTML = '<span>Predicting...</span>';
    setInterval(() => {
      canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData = canvas.toDataURL('image/jpeg');
      socket.emit('frame', { image: imageData, token: jwtToken });
    }, 500); // 2 FPS for performance
  }).catch(() => {
    loader.innerHTML = '<span>Error: Webcam not found.</span>';
  });

  socket.on('prediction', data => {
    let resultDiv = document.getElementById('prediction-result');
    if (!resultDiv) {
      resultDiv = document.createElement('div');
      resultDiv.id = 'prediction-result';
      resultDiv.style.fontSize = '2em';
      resultDiv.style.color = '#232946';
      resultDiv.style.textAlign = 'center';
      document.getElementById('video-to-text').appendChild(resultDiv);
    }
    if (data.error) {
      loader.innerHTML = `<span style='color:red;'>${data.error}</span>`;
    } else {
      loader.innerHTML = '';
      resultDiv.innerHTML = `<span>Prediction: <strong>${data.prediction}</strong></span><br><span>Confidence: <strong>${(data.confidence * 100).toFixed(1)}%</strong></span>`;
      addSpeakButton();
      // Save to history (localStorage for now)
      let history = JSON.parse(localStorage.getItem('prediction_history') || '[]');
      history.push({ time: new Date().toLocaleString(), prediction: data.prediction, confidence: data.confidence });
      localStorage.setItem('prediction_history', JSON.stringify(history));
    }
  });
}

// Add Start Live Demo button
window.addEventListener('DOMContentLoaded', () => {
  const btn = document.createElement('button');
  btn.id = 'startLiveDemoBtn';
  btn.innerText = 'Start Live Demo';
  btn.className = 'inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500';
  btn.setAttribute('aria-label', 'Start Live Sign Language Demo');
  btn.onclick = startLiveDemo;
  document.getElementById('video-to-text').prepend(btn);
});

// Live sign language prediction integration
const socket = io(SOCKET_BASE_URL); // Use dynamic backend IP

const video = document.createElement('video');
video.autoplay = true;
video.width = 320;
video.height = 240;
document.body.appendChild(video);

navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
  video.srcObject = stream;
  const canvas = document.createElement('canvas');
  canvas.width = video.width;
  canvas.height = video.height;

  setInterval(() => {
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/jpeg');
    socket.emit('frame', { image: imageData });
  }, 500); // Send frame every 500ms
});

socket.on('prediction', data => {
  let resultDiv = document.getElementById('prediction-result');
  if (!resultDiv) {
    resultDiv = document.createElement('div');
    resultDiv.id = 'prediction-result';
    resultDiv.style.fontSize = '2em';
    resultDiv.style.color = '#232946';
    document.body.appendChild(resultDiv);
  }
  resultDiv.innerText = data.prediction;
});

// --- History Tab Logic ---
function renderHistory() {
  const historyList = document.getElementById('historyList');
  const noHistory = document.getElementById('noHistory');
  let history = JSON.parse(localStorage.getItem('prediction_history') || '[]');
  historyList.innerHTML = '';
  if (history.length === 0) {
    noHistory.classList.remove('hidden');
    return;
  }
  noHistory.classList.add('hidden');
  history.reverse().forEach(item => {
    const li = document.createElement('li');
    li.className = 'py-4 flex';
    li.innerHTML = `<div class='ml-3'><span class='text-sm font-medium text-gray-900'>${item.prediction}</span><span class='ml-2 text-xs text-gray-500'>${item.time}</span></div>`;
    historyList.appendChild(li);
  });
}

// Show history when tab is clicked
window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab-btn').forEach(tab => {
    tab.addEventListener('click', () => {
      if (tab.dataset.tab === 'history') {
        renderHistory();
      }
    });
  });
});

// --- Feedback Form Logic ---
document.getElementById('feedbackForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const feedbackText = document.getElementById('feedbackText').value.trim();
  let jwtToken = localStorage.getItem('access_token');
  const feedbackMsg = document.getElementById('feedbackMsg');
  if (!feedbackText) {
    feedbackMsg.innerText = 'Please enter your feedback before submitting.';
    feedbackMsg.classList.remove('hidden');
    setTimeout(() => {
      feedbackMsg.classList.add('hidden');
      feedbackMsg.innerText = 'Thank you for your feedback!';
    }, 3000);
    return;
  }
  try {
    const res = await fetch(`${API_BASE_URL}/feedback/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${jwtToken}`
      },
      body: JSON.stringify({
        type: 'general',
        rating: 3,
        comment: feedbackText
      })
    });
    if (res.ok) {
      feedbackMsg.innerText = 'Thank you for your feedback!';
      feedbackMsg.classList.remove('hidden');
      setTimeout(() => {
        feedbackMsg.classList.add('hidden');
        document.getElementById('feedbackText').value = '';
      }, 2000);
    } else {
      feedbackMsg.innerText = 'Error sending feedback.';
      feedbackMsg.classList.remove('hidden');
    }
  } catch {
    feedbackMsg.innerText = 'Error sending feedback.';
    feedbackMsg.classList.remove('hidden');
  }
});

// --- Theme Toggle ---
function toggleTheme() {
  const body = document.body;
  if (body.classList.contains('dark')) {
    body.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  } else {
    body.classList.add('dark');
    localStorage.setItem('theme', 'dark');
  }
}

window.addEventListener('DOMContentLoaded', () => {
  // Theme toggle button
  const themeBtn = document.createElement('button');
  themeBtn.id = 'themeToggleBtn';
  themeBtn.innerText = 'Toggle Theme';
  themeBtn.className = 'inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-indigo-600 bg-white hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500';
  themeBtn.setAttribute('aria-label', 'Toggle dark/light mode');
  themeBtn.onclick = toggleTheme;
  document.querySelector('nav').appendChild(themeBtn);

  // Apply saved theme
  if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark');
  }
});

// --- Accessibility: Keyboard Navigation ---
document.addEventListener('keydown', function(e) {
  if (e.key === 'Tab') {
    document.body.classList.add('user-is-tabbing');
  }
});

// --- Text-to-Speech for Prediction Result ---
function speakPrediction(text) {
  if ('speechSynthesis' in window) {
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'en-US';
    window.speechSynthesis.speak(utter);
  }
}

// Add Speak button next to prediction result
function addSpeakButton() {
  let resultDiv = document.getElementById('prediction-result');
  let speakBtn = document.getElementById('speakBtn');
  if (!speakBtn) {
    speakBtn = document.createElement('button');
    speakBtn.id = 'speakBtn';
    speakBtn.innerText = '🔊 Speak';
    speakBtn.className = 'ml-4 px-3 py-1 rounded bg-indigo-600 text-white hover:bg-indigo-700';
    speakBtn.setAttribute('aria-label', 'Speak prediction');
    speakBtn.onclick = () => {
      const predText = resultDiv ? resultDiv.innerText : '';
      speakPrediction(predText);
    };
    resultDiv && resultDiv.appendChild(speakBtn);
  }
}

// Update prediction display to include Speak button
socket.on('prediction', data => {
  let resultDiv = document.getElementById('prediction-result');
  if (!resultDiv) {
    resultDiv = document.createElement('div');
    resultDiv.id = 'prediction-result';
    resultDiv.style.fontSize = '2em';
    resultDiv.style.color = '#232946';
    resultDiv.style.textAlign = 'center';
    document.getElementById('video-to-text').appendChild(resultDiv);
  }
  if (data.error) {
    loader.innerHTML = `<span style='color:red;'>${data.error}</span>`;
  } else {
    loader.innerHTML = '';
    resultDiv.innerHTML = `<span>Prediction: <strong>${data.prediction}</strong></span><br><span>Confidence: <strong>${(data.confidence * 100).toFixed(1)}%</strong></span>`;
    addSpeakButton();
    // Save to history (localStorage for now)
    let history = JSON.parse(localStorage.getItem('prediction_history') || '[]');
    history.push({ time: new Date().toLocaleString(), prediction: data.prediction, confidence: data.confidence });
    localStorage.setItem('prediction_history', JSON.stringify(history));
  }
});

// Add Tutorials tab logic
window.addEventListener('DOMContentLoaded', () => {
  // Add Tutorials tab button
  const tabsNav = document.querySelector('nav[aria-label="Tabs"]');
  if (tabsNav) {
    const tutorialsBtn = document.createElement('button');
    tutorialsBtn.className = 'tab-btn w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm';
    tutorialsBtn.setAttribute('data-tab', 'tutorials');
    tutorialsBtn.innerHTML = '<i class="fas fa-chalkboard-teacher mr-2"></i>Tutorials';
    tabsNav.appendChild(tutorialsBtn);
  }
});

// Add Community tab button
window.addEventListener('DOMContentLoaded', () => {
  const tabsNav = document.querySelector('nav[aria-label="Tabs"]');
  if (tabsNav) {
    const communityBtn = document.createElement('button');
    communityBtn.className = 'tab-btn w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm';
    communityBtn.setAttribute('data-tab', 'community');
    communityBtn.innerHTML = '<i class="fas fa-users mr-2"></i>Community';
    tabsNav.appendChild(communityBtn);
  }
});

// Community forum logic
function renderCommunity() {
  const communityList = document.getElementById('communityList');
  let posts = JSON.parse(localStorage.getItem('community_posts') || '[]');
  communityList.innerHTML = '';
  posts.reverse().forEach(post => {
    const li = document.createElement('li');
    li.className = 'py-4';
    li.innerHTML = `<div class='text-sm text-gray-900'>${post.text}</div><div class='text-xs text-gray-500'>${post.time}</div>`;
    communityList.appendChild(li);
  });
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('communityForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const msg = document.getElementById('communityMsg').value;
    if (msg.trim()) {
      let posts = JSON.parse(localStorage.getItem('community_posts') || '[]');
      posts.push({ text: msg, time: new Date().toLocaleString() });
      localStorage.setItem('community_posts', JSON.stringify(posts));
      document.getElementById('communityMsg').value = '';
      renderCommunity();
    }
  });
  document.querySelectorAll('.tab-btn').forEach(tab => {
    tab.addEventListener('click', () => {
      if (tab.dataset.tab === 'community') {
        renderCommunity();
      }
    });
  });
});

// Add Admin tab button (visible only to admin)
window.addEventListener('DOMContentLoaded', () => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  if (user && user.role === 'admin') {
    const tabsNav = document.querySelector('nav[aria-label="Tabs"]');
    if (tabsNav) {
      const adminBtn = document.createElement('button');
      adminBtn.className = 'tab-btn w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm';
      adminBtn.setAttribute('data-tab', 'admin');
      adminBtn.innerHTML = '<i class="fas fa-user-shield mr-2"></i>Admin';
      tabsNav.appendChild(adminBtn);
    }
  }
});

// Admin dashboard logic
function renderAdmin() {
  // Example stats from localStorage (replace with backend API in production)
  let history = JSON.parse(localStorage.getItem('prediction_history') || '[]');
  let feedback = JSON.parse(localStorage.getItem('feedback') || '[]');
  let totalPredictions = history.length;
  let avgConfidence = history.length ? (history.reduce((sum, h) => sum + (h.confidence || 0), 0) / history.length) : 0;
  let adminStats = document.getElementById('adminStats');
  adminStats.innerHTML = `<div class='mb-2'>Total Predictions: <strong>${totalPredictions}</strong></div><div class='mb-2'>Average Confidence: <strong>${(avgConfidence * 100).toFixed(1)}%</strong></div>`;
  let adminFeedbackList = document.getElementById('adminFeedbackList');
  adminFeedbackList.innerHTML = '';
  feedback.reverse().forEach(fb => {
    const li = document.createElement('li');
    li.className = 'py-4';
    li.innerHTML = `<div class='text-sm text-gray-900'>${fb.text}</div><div class='text-xs text-gray-500'>${fb.time}</div>`;
    adminFeedbackList.appendChild(li);
  });
}

window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab-btn').forEach(tab => {
    tab.addEventListener('click', () => {
      if (tab.dataset.tab === 'admin') {
        renderAdmin();
      }
    });
  });
});

// --- Admin Dashboard Integration ---
function fetchUsers() {
  let jwtToken = localStorage.getItem('access_token');
  fetch(`${API_BASE_URL}/auth/admin/users`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${jwtToken}`
    }
  })
    .then(res => res.json())
    .then(data => {
      const userList = document.getElementById('userList');
      userList.innerHTML = '';
      if (data.users && data.users.length > 0) {
        data.users.forEach(user => {
          const li = document.createElement('li');
          li.className = 'py-2 flex justify-between';
          li.innerHTML = `<span>${user.username} (${user.email})</span><span>${user.role}</span>`;
          userList.appendChild(li);
        });
      } else {
        userList.innerHTML = '<li class="py-2">No users found.</li>';
      }
      document.getElementById('adminError').classList.add('hidden');
    })
    .catch(err => {
      document.getElementById('adminError').innerText = 'Failed to fetch users.';
      document.getElementById('adminError').classList.remove('hidden');
    });
}

window.addEventListener('DOMContentLoaded', () => {
  const fetchBtn = document.getElementById('fetchUsersBtn');
  if (fetchBtn) {
    fetchBtn.onclick = fetchUsers;
  }
  // Show admin tab only for admin users
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  if (user.role === 'admin') {
    document.querySelector('[data-tab="admin-dashboard"]').style.display = 'block';
  } else {
    document.querySelector('[data-tab="admin-dashboard"]').style.display = 'none';
  }
});

// Add Gamification tab button
window.addEventListener('DOMContentLoaded', () => {
  const tabsNav = document.querySelector('nav[aria-label="Tabs"]');
  if (tabsNav) {
    const gamificationBtn = document.createElement('button');
    gamificationBtn.className = 'tab-btn w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm';
    gamificationBtn.setAttribute('data-tab', 'gamification');
    gamificationBtn.innerHTML = '<i class="fas fa-trophy mr-2"></i>Gamification';
    tabsNav.appendChild(gamificationBtn);
  }
});

// Gamification logic
function renderGamification() {
  // Badges
  let history = JSON.parse(localStorage.getItem('prediction_history') || '[]');
  let feedback = JSON.parse(localStorage.getItem('feedback') || '[]');
  let badgeList = document.getElementById('badgeList');
  badgeList.innerHTML = '';
  if (history.length >= 10) badgeList.innerHTML += '<span class="px-3 py-1 bg-yellow-400 rounded">10 Predictions</span>';
  if (feedback.length >= 5) badgeList.innerHTML += '<span class="px-3 py-1 bg-green-400 rounded">5 Feedbacks</span>';
  // Leaderboard (local, for demo)
  let leaderboardList = document.getElementById('leaderboardList');
  leaderboardList.innerHTML = '';
  let users = [{ name: 'You', score: history.length }, { name: 'User2', score: 8 }, { name: 'User3', score: 5 }];
  users.sort((a, b) => b.score - a.score);
  users.forEach(u => {
    const li = document.createElement('li');
    li.className = 'py-2 flex justify-between';
    li.innerHTML = `<span>${u.name}</span><span>${u.score} pts</span>`;
    leaderboardList.appendChild(li);
  });
  // Quiz
  document.getElementById('quizForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const answer = document.getElementById('quizInput').value.trim().toLowerCase();
    const quizMsg = document.getElementById('quizMsg');
    if (answer === 'fist' || answer === 'closed hand') {
      quizMsg.innerText = 'Correct!';
      quizMsg.classList.remove('hidden');
    } else {
      quizMsg.innerText = 'Try again.';
      quizMsg.classList.remove('hidden');
      quizMsg.classList.add('text-red-600');
    }
    setTimeout(() => quizMsg.classList.add('hidden'), 2000);
  });
}

window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab-btn').forEach(tab => {
    tab.addEventListener('click', () => {
      if (tab.dataset.tab === 'gamification') {
        renderGamification();
      }
    });
  });
});
