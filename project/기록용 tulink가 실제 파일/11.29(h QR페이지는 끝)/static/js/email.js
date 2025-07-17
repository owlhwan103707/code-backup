document.getElementById("email").addEventListener("input", function () {
    const emailInput = this.value;
    const emailPattern = /^[a-zA-Z0-9._%+-]+@yonsei\.ac\.kr$/;

    // 이메일 형식 검사
    if (!emailPattern.test(emailInput)) {
        this.setCustomValidity("이메일 형식이 올바르지 않습니다. @yonsei.ac.kr로 끝나야 합니다.");
    } else {
        this.setCustomValidity(""); // 입력이 유효하면 메시지를 제거합니다.
    }
    this.reportValidity(); // 브라우저가 유효성 검사를 즉시 실행하도록 강제합니다.

    // 이메일 값이 있을 경우, '@yonsei.ac.kr' 자동 추가
    if (emailValue && !emailValue.includes("@yonsei.ac.kr")) {
        emailField.value = emailValue + "@yonsei.ac.kr";
    }
});
