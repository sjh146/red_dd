/**
 * login-interactive.js
 * Pure vanilla JavaScript interactivity for the static Coupang login clone page.
 * No frameworks, no jQuery, no build tools, no network calls.
 *
 * Only external global relied upon: `QRCode` (from a CDN script added separately
 * in login.html). If that CDN fails to load, the page still works — QR generation
 * is simply skipped.
 */
(function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // Module-scoped state
  // ---------------------------------------------------------------------------
  var qrTimerId = null; // setInterval id for the QR countdown
  var qrBuilt = false;  // whether the QR canvas + number have been generated once

  // ---------------------------------------------------------------------------
  // Small DOM helpers
  // ---------------------------------------------------------------------------
  function $(selector, root) {
    return (root || document).querySelector(selector);
  }

  function $$(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function show(el) {
    if (el) { el.style.display = 'block'; }
  }

  function hide(el) {
    if (el) { el.style.display = 'none'; }
  }

  // ---------------------------------------------------------------------------
  // Tab switching
  // ---------------------------------------------------------------------------
  // Map each header tab's data-tab value to its corresponding panel selector.
  // The panels live as direct children of #memberLogin (the .tab-item-content
  // wrapper), NOT as direct children of .member-main.
  var TAB_PANEL_MAP = {
    'password-login': '#memberLogin > .tab-item.member-login',
    'pc-otp-login-v4': '#memberLogin > .tab-item.pc-otp-login-v4',
    'qr-login': '#memberLogin > .tab-item.qr-login'
  };

  function getPanels() {
    return {
      'password-login': $(TAB_PANEL_MAP['password-login']),
      'pc-otp-login-v4': $(TAB_PANEL_MAP['pc-otp-login-v4']),
      'qr-login': $(TAB_PANEL_MAP['qr-login'])
    };
  }

  function switchTab(tabKey) {
    var panels = getPanels();
    var headerTabs = $$('.tab-item-header > a[data-tab]');

    // Update header active state.
    headerTabs.forEach(function (tab) {
      if (tab.getAttribute('data-tab') === tabKey) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });

    // Hide all panels.
    Object.keys(panels).forEach(function (key) {
      hide(panels[key]);
    });

    // Show the target panel (keyed by the actual data-tab value).
    var target = panels[tabKey];
    if (target) {
      show(target);
    }

    // Lazily build the QR + start the timer the first time the QR tab opens.
    if (tabKey === 'qr-login') {
      if (!qrBuilt) {
        buildQr();
        startQrTimer();
      }
    }
  }

  // ---------------------------------------------------------------------------
  // QR generation (lazy, once)
  // ---------------------------------------------------------------------------
  function randomNumber() {
    return Math.floor(1000 + Math.random() * 9000);
  }

  function buildQr() {
    var qrImage = $('.qr-login__image');
    var qrNumber = $('.qr-login__number');
    if (!qrImage) { return; }

    // Avoid duplicate generation on re-entry.
    if (qrImage.querySelector('canvas')) {
      return;
    }

    // Set the 4-digit confirm number.
    if (qrNumber) {
      qrNumber.textContent = String(randomNumber());
    }

    // Only generate a QR if the CDN library is available.
    if (typeof QRCode !== 'undefined') {
      try {
        new QRCode(qrImage, {
          text: 'http://127.0.0.1/coupang/qr-session-' + Date.now(),
          width: 160,
          height: 160,
          colorDark: '#000000',
          colorLight: '#ffffff',
          correctLevel: QRCode.CorrectLevel.M
        });
      } catch (e) {
        // Never throw on normal use; QR is a progressive enhancement.
      }
    }

    qrBuilt = true;
  }

  // ---------------------------------------------------------------------------
  // QR timer
  // ---------------------------------------------------------------------------
  function formatTime(totalSeconds) {
    var minutes = Math.floor(totalSeconds / 60);
    var seconds = totalSeconds % 60;
    return minutes + ':' + (seconds < 10 ? '0' + seconds : String(seconds));
  }

  function startQrTimer() {
    var timerEl = $('.qr-login__timer .timer');
    var content = $('.qr-login__content');
    var timeoff = $('.qr-login__timeoff');
    if (!timerEl) { return; }

    // Clear any previous interval to avoid duplicates.
    if (qrTimerId !== null) {
      clearInterval(qrTimerId);
      qrTimerId = null;
    }

    var remaining = 180; // 3:00
    timerEl.textContent = formatTime(remaining);

    qrTimerId = setInterval(function () {
      remaining -= 1;

      if (remaining <= 0) {
        clearInterval(qrTimerId);
        qrTimerId = null;
        timerEl.textContent = formatTime(0);
        hide(content);
        show(timeoff);
        return;
      }

      timerEl.textContent = formatTime(remaining);
    }, 1000);
  }

  // ---------------------------------------------------------------------------
  // QR retry
  // ---------------------------------------------------------------------------
  function retryQr() {
    var qrImage = $('.qr-login__image');
    var qrNumber = $('.qr-login__number');
    var content = $('.qr-login__content');
    var timeoff = $('.qr-login__timeoff');

    // Clear any running timer.
    if (qrTimerId !== null) {
      clearInterval(qrTimerId);
      qrTimerId = null;
    }

    // Show content, hide the timeoff notice.
    show(content);
    hide(timeoff);

    // Clear the old QR canvas and regenerate a fresh one.
    if (qrImage) {
      qrImage.innerHTML = '';
    }
    if (qrNumber) {
      qrNumber.textContent = String(randomNumber());
    }

    if (typeof QRCode !== 'undefined') {
      try {
        new QRCode(qrImage, {
          text: 'http://127.0.0.1/coupang/qr-session-' + Date.now(),
          width: 160,
          height: 160,
          colorDark: '#000000',
          colorLight: '#ffffff',
          correctLevel: QRCode.CorrectLevel.M
        });
      } catch (e) {
        // Ignore; QR is a progressive enhancement.
      }
    }

    qrBuilt = true;
    startQrTimer();
  }

  // ---------------------------------------------------------------------------
  // Email form submit
  // ---------------------------------------------------------------------------
  function handleLoginSubmit(event) {
    event.preventDefault();

    var emailInput = $('#login-email-input');
    var passwordInput = $('#login-password-input');
    var errorEl = $('._loginCommonError');

    var emailEmpty = !emailInput || !emailInput.value.trim();
    var passwordEmpty = !passwordInput || !passwordInput.value;

    if (emailEmpty || passwordEmpty) {
      if (errorEl) {
        errorEl.textContent = '아이디와 비밀번호를 입력해주세요.';
        show(errorEl);
      }
      return;
    }

    // Both filled: do nothing further (no real login).
  }

  // ---------------------------------------------------------------------------
  // Phone auth button
  // ---------------------------------------------------------------------------
  function handlePhoneSubmit() {
    var phoneInput = $('._phoneInput');
    var errorEl = $('#phone-field-wrap .error-message');
    var value = phoneInput ? phoneInput.value.replace(/\D/g, '') : '';

    if (!errorEl) { return; }

    if (!value || value.length < 10 || value.length > 11) {
      errorEl.textContent = '휴대폰번호를 입력해주세요.';
      show(errorEl);
      return;
    }

    errorEl.textContent = '';
    hide(errorEl);
    errorEl.textContent = '인증번호를 발송했습니다.';
    show(errorEl);
  }

  // ---------------------------------------------------------------------------
  // Password show/hide
  // ---------------------------------------------------------------------------
  function handlePasswordToggle() {
    var passwordInput = $('#login-password-input');
    var openedEye = $('._loginPasswordIconOpenedEye');
    var closedEye = $('._loginPasswordIconClosedEye');
    if (!passwordInput) { return; }

    var isHidden = passwordInput.type === 'password';
    passwordInput.type = isHidden ? 'text' : 'password';

    if (openedEye) { openedEye.style.display = isHidden ? 'none' : ''; }
    if (closedEye) { closedEye.style.display = isHidden ? '' : 'none'; }
  }

  // ---------------------------------------------------------------------------
  // ID clear
  // ---------------------------------------------------------------------------
  function handleIdClear() {
    var emailInput = $('#login-email-input');
    if (emailInput) {
      emailInput.value = '';
      emailInput.focus();
    }
  }

  // ---------------------------------------------------------------------------
  // Wire up all listeners
  // ---------------------------------------------------------------------------
  function init() {

    // Tab switching.
    $$('.tab-item-header > a[data-tab]').forEach(function (tab) {
      tab.addEventListener('click', function () {
        switchTab(tab.getAttribute('data-tab'));
      });
    });

    // Email form submit.
    var loginForm = $('.login__form');
    if (loginForm) {
      loginForm.addEventListener('submit', handleLoginSubmit);
    }

    // Phone auth button.
    var phoneSubmit = $('._phoneSubmitButton');
    if (phoneSubmit) {
      phoneSubmit.addEventListener('click', function (event) {
        event.preventDefault();
        handlePhoneSubmit();
      });
    }

    // Password show/hide.
    var passwordToggle = $('._loginPasswordShowTrigger');
    if (passwordToggle) {
      passwordToggle.addEventListener('click', handlePasswordToggle);
    }

    // ID clear.
    var idClear = $('._loginIdClear');
    if (idClear) {
      idClear.addEventListener('click', handleIdClear);
    }

    // QR retry.
    var refresh = $('._refresh');
    if (refresh) {
      refresh.addEventListener('click', function (event) {
        event.preventDefault();
        retryQr();
      });
    }
  }

  // ---------------------------------------------------------------------------
  // Boot: run on DOMContentLoaded, or immediately if the DOM is already ready.
  // ---------------------------------------------------------------------------
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
