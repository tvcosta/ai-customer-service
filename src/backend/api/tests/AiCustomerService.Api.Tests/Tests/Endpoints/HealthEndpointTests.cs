using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using AiCustomerService.Api.Endpoints.Health;
using FluentAssertions;
using NSubstitute;
using NSubstitute.ExceptionExtensions;
using Xunit;

namespace AiCustomerService.Api.Tests.Tests.Endpoints;

public sealed class HealthEndpointTests : IClassFixture<ApiTestFactory>
{
    private readonly ApiTestFactory _factory;
    private readonly HttpClient _client;

    public HealthEndpointTests(ApiTestFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetHealth_WhenCoreIsReachable_Returns200WithHealthyStatus()
    {
        // Arrange
        _factory.CoreApiClient
            .CheckHealthAsync(Arg.Any<CancellationToken>())
            .Returns(true);

        // Act
        var response = await _client.GetAsync("/api/v1/health");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<HealthResponseDto>(
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

        body.Should().NotBeNull();
        body!.Status.Should().Be("healthy");
        body.CoreStatus.Should().Be("healthy");
    }

    [Fact]
    public async Task GetHealth_WhenCoreReturnsFalse_Returns200WithUnreachableCoreStatus()
    {
        // Arrange
        _factory.CoreApiClient
            .CheckHealthAsync(Arg.Any<CancellationToken>())
            .Returns(false);

        // Act
        var response = await _client.GetAsync("/api/v1/health");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<HealthResponseDto>(
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

        body.Should().NotBeNull();
        body!.Status.Should().Be("healthy");
        body.CoreStatus.Should().Be("unreachable");
    }

    [Fact]
    public async Task GetHealth_WhenCoreThrowsException_Returns200WithUnreachableCoreStatus()
    {
        // Arrange
        _factory.CoreApiClient
            .CheckHealthAsync(Arg.Any<CancellationToken>())
            .ThrowsAsync(new HttpRequestException("Connection refused"));

        // Act
        var response = await _client.GetAsync("/api/v1/health");

        // Assert – the health endpoint NEVER returns non-2xx; it absorbs errors gracefully
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<HealthResponseDto>(
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

        body.Should().NotBeNull();
        body!.Status.Should().Be("healthy");
        body.CoreStatus.Should().Be("unreachable");
    }
}
