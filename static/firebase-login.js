'use strict';

// Import Firebase modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";

// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyDx16dcjXdszV6luS7dbE-ZA_Znm5htoZQ",
    authDomain: "f1-formula-453723.firebaseapp.com",
    projectId: "f1-formula-453723",
    storageBucket: "f1-formula-453723.firebasestorage.app",
    messagingSenderId: "546526556738",
    appId: "1:546526556738:web:7ff7d8e0f8adde377773db"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Function to update UI based on authentication state
function updateUI() {
    const token = parseCookieToken(document.cookie);

    if (token.length > 0) {
        document.getElementById("login-box").hidden = true;
        document.getElementById("sign-out").hidden = false;
    } else {
        document.getElementById("login-box").hidden = false;
        document.getElementById("sign-out").hidden = true;
    }
}

// Function to parse the authentication token from cookies
function parseCookieToken(cookie) {
    const strings = cookie.split(';');
    for (let i = 0; i < strings.length; i++) {
        let temp = strings[i].trim().split('=');
        if (temp[0] === "token") {
            return temp[1];
        }
    }
    return "";
}

// Event listener to execute on page load
window.addEventListener("load", function () {
    updateUI(); 
    console.log("Firebase Authentication Loaded");

    // Signup new user
    document.getElementById("sign-up").addEventListener('click', function () {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        createUserWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                const user = userCredential.user;
                return user.getIdToken();
            })
            .then((token) => {
                document.cookie = `token=${token}; path=/; SameSite=Strict`;
                window.location = "/";
            })
            .catch((error) => {
                console.error("Signup Error:", error.code, error.message);
            });
    });

    // Login existing user
    document.getElementById("login").addEventListener('click', function () {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        signInWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                const user = userCredential.user;
                console.log("Logged in");

                return user.getIdToken();
            })
            .then((token) => {
                document.cookie = `token=${token}; path=/; SameSite=Strict`;
                window.location = "/";
            })
            .catch((error) => {
                console.error("Login Error:", error.code, error.message);
            });
    });

    // Logout user
    document.getElementById("sign-out").addEventListener('click', function () {
        signOut(auth)
            .then(() => {
                document.cookie = "token=; path=/; SameSite=Strict";
                window.location = "/";
            })
            .catch((error) => {
                console.error("Logout Error:", error.code, error.message);
            });
    });
});
