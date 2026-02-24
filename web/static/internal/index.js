const search = (searchTerm) => {
  const channels = document.querySelectorAll('.card');
  const normalizedTerm = searchTerm.trim().toLowerCase();
  let visibleCount = 0;

  // Update URL search parameter
  updateUrlParameter('search', normalizedTerm);

  channels.forEach((channel) => {
    const nameElement = channel.querySelector('.font-bold');
    if (nameElement) {
      const name = nameElement.textContent.toLowerCase();
      const isVisible = normalizedTerm === '' || name.includes(normalizedTerm);
      channel.style.display = isVisible ? 'block' : 'none';
      if (isVisible) {
        visibleCount += 1;
      }
    }
  });

  const emptyState = safeGetElementById('portexe-empty-state', true);
  if (emptyState) {
    if (visibleCount === 0 && normalizedTerm !== '') {
      emptyState.classList.remove('hidden');
    } else {
      emptyState.classList.add('hidden');
    }
  }
};

const init = () => {
  const searchInput = safeGetElementById('portexe-search-input');
  let searchDebounceTimer = null;

  // Check for search parameter on page load
  const urlParams = getCurrentUrlParams();
  const searchParam = urlParams.get('search');

  if (searchParam && searchInput) {
    const trimmed = searchParam.trim();
    search(trimmed);
    searchInput.value = trimmed;
  } else {
    search('');
  }

  if (searchInput) {
    searchInput.addEventListener('keyup', (e) => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        search(e.target.value);
      }, 120);
    });

    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        searchInput.value = '';
        search('');
      }
    });
  }
};

// Call the init function to start the process
init();



const loginOTPClick = () => {
  const numberElement = safeGetElementById("number");
  if (!numberElement) {
    return;
  }

  const number = numberElement.value;
  if (!number) {
    return;
  }

  postJSON("/login/sendOTP", { number: `+91${number}` })
    .then((data) => {
      if (data.status) {
        verify_otp_modal.showModal(); // skipcq: JS-0125
      } else {
        alert("Sending OTP failed!");
      }
    })
    .catch((err) => {
      console.log(err);
      alert("Sending OTP failed!");
    });
};

const loginOTPVerifyClick = () => {
  const elements = safeGetElementsById(["number", "otp"]);
  const { number: numberElement, otp: otpElement } = elements;

  if (!numberElement || !otpElement) {
    return;
  }

  const number = numberElement.value;
  const otp = otpElement.value;

  if (!number || !otp) {
    return;
  }

  postJSON("/login/verifyOTP", { number: `+91${number}`, otp })
    .then((data) => {
      if (data.status) {
        alert("OTP verification success. Enjoy!");
        document.location.reload();
      } else {
        alert("OTP verification failed!");
      }
    })
    .catch((err) => {
      console.log(err);
      alert("OTP verification failed!");
    });
};
