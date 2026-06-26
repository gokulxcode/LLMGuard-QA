package com.llmguard.qa;

import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.testng.Assert;
import org.testng.annotations.Test;

public class LoginTest extends BaseTest {

    @Test
    public void testSuccessfulLogin() {
        driver.get(baseUrl + "/login");

        // Locate input elements
        WebElement usernameInput = driver.findElement(By.cssSelector("input[placeholder='Enter admin or tester username']"));
        WebElement passwordInput = driver.findElement(By.cssSelector("input[placeholder='••••••••']"));
        WebElement loginButton = driver.findElement(By.xpath("//button[contains(text(),'Sign In')]"));

        // Type credentials
        usernameInput.sendKeys("admin");
        passwordInput.sendKeys("adminpassword");
        loginButton.click();

        // Check if URL redirects to dashboard
        String currentUrl = driver.getCurrentUrl();
        Assert.assertTrue(currentUrl.contains("/dashboard"), "Expected redirection to dashboard page. Got: " + currentUrl);
    }

    @Test
    public void testFailedLogin() {
        driver.get(baseUrl + "/login");

        WebElement usernameInput = driver.findElement(By.cssSelector("input[placeholder='Enter admin or tester username']"));
        WebElement passwordInput = driver.findElement(By.cssSelector("input[placeholder='••••••••']"));
        WebElement loginButton = driver.findElement(By.xpath("//button[contains(text(),'Sign In')]"));

        // Type invalid credentials
        usernameInput.sendKeys("invalid_user");
        passwordInput.sendKeys("badpassword");
        loginButton.click();

        // Check for error element presentation
        WebElement errorAlert = driver.findElement(By.xpath("//div[contains(@class, 'text-red-400')]"));
        Assert.assertNotNull(errorAlert, "Error notification alert should render on screen");
        Assert.assertTrue(errorAlert.getText().contains("Incorrect username or password"), "Incorrect error message displayed.");
    }
}
