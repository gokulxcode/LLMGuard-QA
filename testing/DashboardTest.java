package com.llmguard.qa;

import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.testng.Assert;
import org.testng.annotations.Test;

public class DashboardTest extends BaseTest {

    @Test
    public void testDashboardStatCards() {
        // Log in first to access secured views
        driver.get(baseUrl + "/login");
        driver.findElement(By.cssSelector("input[placeholder='Enter admin or tester username']")).sendKeys("admin");
        driver.findElement(By.cssSelector("input[placeholder='••••••••']")).sendKeys("adminpassword");
        driver.findElement(By.xpath("//button[contains(text(),'Sign In')]")).click();

        // Navigate to dashboard
        driver.get(baseUrl + "/dashboard");

        // Verify Title header
        WebElement headerElement = driver.findElement(By.xpath("//h1[text()='QA Metrics Dashboard']"));
        Assert.assertNotNull(headerElement, "Dashboard title is missing");

        // Verify KPI cards
        WebElement testsCard = driver.findElement(By.xpath("//span[text()='Total Tests Run']"));
        WebElement hallucinationsCard = driver.findElement(By.xpath("//span[text()='Hallucinations Found']"));
        WebElement safetyCard = driver.findElement(By.xpath("//span[text()='Safety Issues Alerted']"));
        WebElement leakageCard = driver.findElement(By.xpath("//span[text()='Context Leakage Detected']"));

        Assert.assertNotNull(testsCard, "Total Tests KPI card is missing");
        Assert.assertNotNull(hallucinationsCard, "Hallucinations KPI card is missing");
        Assert.assertNotNull(safetyCard, "Safety alerts KPI card is missing");
        Assert.assertNotNull(leakageCard, "Privacy leakage KPI card is missing");
    }
}
