using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using AiCustomerService.Api.Application.Services;
using AiCustomerService.Api.Domain.Models;
using FluentAssertions;
using Xunit;

namespace AiCustomerService.Api.Tests.Tests.Infrastructure;

/// <summary>
/// Unit tests for <see cref="CoreApiClient"/> focusing on JSON serialization/deserialization
/// of request and response payloads.  These tests use a fake HttpMessageHandler so no
/// real network connections are made.
/// </summary>
public sealed class CoreApiClientTests
{
    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private static CoreApiClient BuildClient(HttpMessageHandler handler)
    {
        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new Uri("http://localhost:8000")
        };
        return new CoreApiClient(httpClient);
    }

    private static FakeHttpMessageHandler RespondWith(object body, HttpStatusCode status = HttpStatusCode.OK)
    {
        var json = JsonSerializer.Serialize(body);
        return new FakeHttpMessageHandler(status, json, "application/json");
    }

    // -------------------------------------------------------------------------
    // QueryAsync
    // -------------------------------------------------------------------------

    [Fact]
    public async Task QueryAsync_SerializesRequestWithSnakeCasePropertyNames()
    {
        // Arrange
        var capturedContent = string.Empty;
        var responsePayload = new
        {
            status = "answered",
            answer = "Test answer",
            citations = (object?)null,
            interaction_id = Guid.NewGuid().ToString(),
            error = (object?)null
        };

        var handler = new CapturingHttpMessageHandler(
            JsonSerializer.Serialize(responsePayload),
            content => capturedContent = content);

        var client = BuildClient(handler);
        var request = new QueryRequestDto("kb-001", "What is the warranty?");

        // Act
        await client.QueryAsync(request);

        // Assert – the wire format uses snake_case keys
        var doc = JsonDocument.Parse(capturedContent);
        doc.RootElement.TryGetProperty("knowledge_base_id", out var kbId).Should().BeTrue();
        kbId.GetString().Should().Be("kb-001");

        doc.RootElement.TryGetProperty("question", out var question).Should().BeTrue();
        question.GetString().Should().Be("What is the warranty?");
    }

    [Fact]
    public async Task QueryAsync_DeserializesResponseCorrectly()
    {
        // Arrange
        var interactionId = Guid.NewGuid().ToString();
        var responsePayload = new
        {
            status = "answered",
            answer = "The warranty is 2 years.",
            citations = new[]
            {
                new { source_document = "manual.pdf", page = 3, chunk_id = "chunk-001", relevance_score = 0.95 }
            },
            interaction_id = interactionId,
            error = (string?)null
        };

        var client = BuildClient(RespondWith(responsePayload));

        // Act
        var result = await client.QueryAsync(new QueryRequestDto("kb-001", "Question?"));

        // Assert
        result.Status.Should().Be("answered");
        result.Answer.Should().Be("The warranty is 2 years.");
        result.InteractionId.Should().Be(interactionId);
        result.Citations.Should().HaveCount(1);
        result.Citations![0].SourceDocument.Should().Be("manual.pdf");
        result.Citations[0].Page.Should().Be(3);
        result.Citations[0].ChunkId.Should().Be("chunk-001");
        result.Citations[0].RelevanceScore.Should().BeApproximately(0.95, 0.001);
    }

    [Fact]
    public async Task QueryAsync_WhenCoreReturnsUnknown_DeserializesNullFields()
    {
        // Arrange
        var interactionId = Guid.NewGuid().ToString();
        var responsePayload = new
        {
            status = "unknown",
            answer = (string?)null,
            citations = (object?)null,
            interaction_id = interactionId,
            error = (string?)null
        };

        var client = BuildClient(RespondWith(responsePayload));

        // Act
        var result = await client.QueryAsync(new QueryRequestDto("kb-001", "Question?"));

        // Assert
        result.Status.Should().Be("unknown");
        result.Answer.Should().BeNull();
        result.Citations.Should().BeNull();
    }

    // -------------------------------------------------------------------------
    // KnowledgeBase serialization
    // -------------------------------------------------------------------------

    [Fact]
    public async Task ListKnowledgeBasesAsync_DeserializesListCorrectly()
    {
        // Arrange
        var createdAt = new DateTime(2025, 1, 15, 10, 30, 0, DateTimeKind.Utc);
        var responsePayload = new[]
        {
            new { id = "kb-001", name = "Manual KB", description = (string?)"Product manuals", created_at = createdAt },
            new { id = "kb-002", name = "FAQ KB", description = (string?)null, created_at = createdAt },
        };

        var client = BuildClient(RespondWith(responsePayload));

        // Act
        var result = await client.ListKnowledgeBasesAsync();

        // Assert
        result.Should().HaveCount(2);
        result[0].Id.Should().Be("kb-001");
        result[0].Name.Should().Be("Manual KB");
        result[0].Description.Should().Be("Product manuals");
        result[1].Id.Should().Be("kb-002");
        result[1].Description.Should().BeNull();
    }

    [Fact]
    public async Task CreateKnowledgeBaseAsync_SerializesRequestWithSnakeCaseKeys()
    {
        // Arrange
        var capturedContent = string.Empty;
        var responsePayload = new { id = "kb-new", name = "New KB", description = "Desc", created_at = DateTime.UtcNow };

        var handler = new CapturingHttpMessageHandler(
            JsonSerializer.Serialize(responsePayload),
            content => capturedContent = content);

        var client = BuildClient(handler);
        var request = new CreateKnowledgeBaseRequestDto("New KB", "Desc");

        // Act
        await client.CreateKnowledgeBaseAsync(request);

        // Assert – wire format uses snake_case
        var doc = JsonDocument.Parse(capturedContent);
        doc.RootElement.TryGetProperty("name", out var name).Should().BeTrue();
        name.GetString().Should().Be("New KB");

        doc.RootElement.TryGetProperty("description", out var description).Should().BeTrue();
        description.GetString().Should().Be("Desc");
    }

    // -------------------------------------------------------------------------
    // Interaction serialization
    // -------------------------------------------------------------------------

    [Fact]
    public async Task GetInteractionAsync_DeserializesInteractionCorrectly()
    {
        // Arrange
        var createdAt = new DateTime(2025, 2, 1, 9, 0, 0, DateTimeKind.Utc);
        var responsePayload = new
        {
            id = "int-001",
            kb_id = "kb-001",
            question = "What is the warranty?",
            answer = "2 years.",
            status = "answered",
            citations = new[]
            {
                new { source_document = "doc.pdf", page = (int?)1, chunk_id = "c1", relevance_score = 0.88 }
            },
            created_at = createdAt
        };

        var client = BuildClient(RespondWith(responsePayload));

        // Act
        var result = await client.GetInteractionAsync("int-001");

        // Assert
        result.Id.Should().Be("int-001");
        result.KbId.Should().Be("kb-001");
        result.Question.Should().Be("What is the warranty?");
        result.Answer.Should().Be("2 years.");
        result.Status.Should().Be("answered");
        result.Citations.Should().HaveCount(1);
        result.Citations![0].SourceDocument.Should().Be("doc.pdf");
    }

    // -------------------------------------------------------------------------
    // CheckHealthAsync
    // -------------------------------------------------------------------------

    [Fact]
    public async Task CheckHealthAsync_WhenCoreReturns200_ReturnsTrue()
    {
        // Arrange
        var handler = new FakeHttpMessageHandler(HttpStatusCode.OK, "{}", "application/json");
        var client = BuildClient(handler);

        // Act
        var result = await client.CheckHealthAsync();

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task CheckHealthAsync_WhenCoreReturns503_ReturnsFalse()
    {
        // Arrange
        var handler = new FakeHttpMessageHandler(HttpStatusCode.ServiceUnavailable, "{}", "application/json");
        var client = BuildClient(handler);

        // Act
        var result = await client.CheckHealthAsync();

        // Assert
        result.Should().BeFalse();
    }

    // -------------------------------------------------------------------------
    // DashboardStats serialization
    // -------------------------------------------------------------------------

    [Fact]
    public async Task GetDashboardStatsAsync_DeserializesStatsCorrectly()
    {
        // Arrange
        var responsePayload = new
        {
            total_interactions = 150,
            answered_count = 120,
            unknown_count = 30,
            knowledge_base_count = 5,
            document_count = 42
        };

        var client = BuildClient(RespondWith(responsePayload));

        // Act
        var result = await client.GetDashboardStatsAsync();

        // Assert
        result.TotalInteractions.Should().Be(150);
        result.AnsweredCount.Should().Be(120);
        result.UnknownCount.Should().Be(30);
        result.KnowledgeBaseCount.Should().Be(5);
        result.DocumentCount.Should().Be(42);
    }
}

// -------------------------------------------------------------------------
// Test doubles
// -------------------------------------------------------------------------

/// <summary>
/// Simple fake HttpMessageHandler that always returns a fixed response.
/// </summary>
internal sealed class FakeHttpMessageHandler : HttpMessageHandler
{
    private readonly HttpStatusCode _statusCode;
    private readonly string _responseBody;
    private readonly string _contentType;

    public FakeHttpMessageHandler(HttpStatusCode statusCode, string responseBody, string contentType)
    {
        _statusCode = statusCode;
        _responseBody = responseBody;
        _contentType = contentType;
    }

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var response = new HttpResponseMessage(_statusCode)
        {
            Content = new StringContent(_responseBody, System.Text.Encoding.UTF8, _contentType)
        };
        return Task.FromResult(response);
    }
}

/// <summary>
/// HttpMessageHandler that captures the request body and returns a fixed 200 response.
/// </summary>
internal sealed class CapturingHttpMessageHandler : HttpMessageHandler
{
    private readonly string _responseBody;
    private readonly Action<string> _captureCallback;

    public CapturingHttpMessageHandler(string responseBody, Action<string> captureCallback)
    {
        _responseBody = responseBody;
        _captureCallback = captureCallback;
    }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        if (request.Content is not null)
        {
            var content = await request.Content.ReadAsStringAsync(cancellationToken);
            _captureCallback(content);
        }

        return new HttpResponseMessage(HttpStatusCode.OK)
        {
            Content = new StringContent(_responseBody, System.Text.Encoding.UTF8, "application/json")
        };
    }
}
