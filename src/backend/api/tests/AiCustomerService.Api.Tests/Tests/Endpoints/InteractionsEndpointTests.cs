using System.Net;
using System.Net.Http.Json;
using AiCustomerService.Api.Domain.Models;
using FluentAssertions;
using NSubstitute;
using Xunit;

namespace AiCustomerService.Api.Tests.Tests.Endpoints;

public sealed class InteractionsEndpointTests : IClassFixture<ApiTestFactory>
{
    private readonly ApiTestFactory _factory;
    private readonly HttpClient _client;

    public InteractionsEndpointTests(ApiTestFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    // -------------------------------------------------------------------------
    // LIST interactions
    // -------------------------------------------------------------------------

    [Fact]
    public async Task GetInteractions_Returns200WithList()
    {
        // Arrange
        var now = DateTime.UtcNow;
        var interactions = new List<InteractionDto>
        {
            new("int-001", "kb-001", "What is the warranty?", "2 years.", "answered",
                [new CitationDto("manual.pdf", 1, "chunk-1", 0.9)], now),
            new("int-002", "kb-001", "What is the capital of Mars?", null, "unknown", null, now),
        };

        _factory.CoreApiClient
            .ListInteractionsAsync(Arg.Any<CancellationToken>())
            .Returns(interactions);

        // Act
        var response = await _client.GetAsync("/api/v1/interactions");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<List<InteractionDto>>();
        body.Should().NotBeNull();
        body.Should().HaveCount(2);
        body![0].Id.Should().Be("int-001");
        body[0].Status.Should().Be("answered");
        body[1].Id.Should().Be("int-002");
        body[1].Status.Should().Be("unknown");
        body[1].Answer.Should().BeNull();
    }

    [Fact]
    public async Task GetInteractions_WhenNoneExist_Returns200WithEmptyArray()
    {
        // Arrange
        _factory.CoreApiClient
            .ListInteractionsAsync(Arg.Any<CancellationToken>())
            .Returns(new List<InteractionDto>());

        // Act
        var response = await _client.GetAsync("/api/v1/interactions");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<List<InteractionDto>>();
        body.Should().NotBeNull().And.BeEmpty();
    }

    // -------------------------------------------------------------------------
    // GET interaction by ID
    // -------------------------------------------------------------------------

    [Fact]
    public async Task GetInteraction_WithValidId_Returns200WithInteraction()
    {
        // Arrange
        var now = DateTime.UtcNow;
        var interaction = new InteractionDto(
            "int-001", "kb-001",
            "What is the warranty?", "2 years.",
            "answered",
            [new CitationDto("manual.pdf", 2, "chunk-42", 0.97)],
            now);

        _factory.CoreApiClient
            .GetInteractionAsync("int-001", Arg.Any<CancellationToken>())
            .Returns(interaction);

        // Act
        var response = await _client.GetAsync("/api/v1/interactions/int-001");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<InteractionDto>();
        body.Should().NotBeNull();
        body!.Id.Should().Be("int-001");
        body.KbId.Should().Be("kb-001");
        body.Question.Should().Be("What is the warranty?");
        body.Answer.Should().Be("2 years.");
        body.Status.Should().Be("answered");
        body.Citations.Should().HaveCount(1);
        body.Citations![0].SourceDocument.Should().Be("manual.pdf");
    }

    [Fact]
    public async Task GetInteraction_PassesCorrectIdToClient()
    {
        // Arrange
        var capturedId = string.Empty;
        var interaction = new InteractionDto(
            "int-xyz", "kb-001", "Question", "Answer", "answered", null, DateTime.UtcNow);

        _factory.CoreApiClient
            .GetInteractionAsync(
                Arg.Do<string>(id => capturedId = id),
                Arg.Any<CancellationToken>())
            .Returns(interaction);

        // Act
        await _client.GetAsync("/api/v1/interactions/int-xyz");

        // Assert
        capturedId.Should().Be("int-xyz");
    }

    [Fact]
    public async Task GetInteraction_WithUnknownStatus_Returns200WithNullAnswer()
    {
        // Arrange
        var interaction = new InteractionDto(
            "int-003", "kb-002", "What is the meaning of life?", null,
            "unknown", null, DateTime.UtcNow);

        _factory.CoreApiClient
            .GetInteractionAsync("int-003", Arg.Any<CancellationToken>())
            .Returns(interaction);

        // Act
        var response = await _client.GetAsync("/api/v1/interactions/int-003");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<InteractionDto>();
        body.Should().NotBeNull();
        body!.Status.Should().Be("unknown");
        body.Answer.Should().BeNull();
        body.Citations.Should().BeNullOrEmpty();
    }
}
