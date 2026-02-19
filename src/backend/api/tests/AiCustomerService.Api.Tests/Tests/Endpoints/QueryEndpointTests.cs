using System.Net;
using System.Net.Http.Json;
using AiCustomerService.Api.Domain.Models;
using FluentAssertions;
using NSubstitute;
using NSubstitute.ExceptionExtensions;
using Xunit;

namespace AiCustomerService.Api.Tests.Tests.Endpoints;

public sealed class QueryEndpointTests : IClassFixture<ApiTestFactory>
{
    private readonly ApiTestFactory _factory;
    private readonly HttpClient _client;

    public QueryEndpointTests(ApiTestFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
        // Clear any recorded calls from previous tests in this fixture
        _factory.CoreApiClient.ClearReceivedCalls();
    }

    [Fact]
    public async Task PostQuery_WithValidRequest_Returns200WithAnsweredStatus()
    {
        // Arrange
        var interactionId = Guid.NewGuid().ToString();
        var expectedResponse = new QueryResponseDto(
            Status: "answered",
            Answer: "The warranty is 2 years.",
            Citations: [new CitationDto("manual.pdf", 3, "chunk-001", 0.95)],
            InteractionId: interactionId,
            Error: null);

        _factory.CoreApiClient
            .QueryAsync(Arg.Any<QueryRequestDto>(), Arg.Any<CancellationToken>())
            .Returns(expectedResponse);

        var request = new { knowledge_base_id = "kb-001", question = "What is the warranty period?" };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/query", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<QueryResponseDto>();
        body.Should().NotBeNull();
        body!.Status.Should().Be("answered");
        body.Answer.Should().Be("The warranty is 2 years.");
        body.InteractionId.Should().Be(interactionId);
        body.Citations.Should().HaveCount(1);
        body.Citations![0].SourceDocument.Should().Be("manual.pdf");
        body.Citations[0].ChunkId.Should().Be("chunk-001");
    }

    [Fact]
    public async Task PostQuery_WhenCoreReturnsUnknown_Returns200WithUnknownStatus()
    {
        // Arrange
        var interactionId = Guid.NewGuid().ToString();
        var expectedResponse = new QueryResponseDto(
            Status: "unknown",
            Answer: null,
            Citations: null,
            InteractionId: interactionId,
            Error: null);

        _factory.CoreApiClient
            .QueryAsync(Arg.Any<QueryRequestDto>(), Arg.Any<CancellationToken>())
            .Returns(expectedResponse);

        var request = new { knowledge_base_id = "kb-001", question = "What is the meaning of life?" };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/query", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<QueryResponseDto>();
        body.Should().NotBeNull();
        body!.Status.Should().Be("unknown");
        body.Answer.Should().BeNull();
        body.Citations.Should().BeNullOrEmpty();
    }

    [Fact]
    public async Task PostQuery_WithEmptyKnowledgeBaseId_Returns400ValidationError()
    {
        // Arrange
        var request = new { knowledge_base_id = "", question = "What is the warranty period?" };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/query", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);

        // Verify the mock was never called - validation should short-circuit
        await _factory.CoreApiClient
            .DidNotReceive()
            .QueryAsync(Arg.Any<QueryRequestDto>(), Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task PostQuery_WithEmptyQuestion_Returns400ValidationError()
    {
        // Arrange
        var request = new { knowledge_base_id = "kb-001", question = "" };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/query", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);

        await _factory.CoreApiClient
            .DidNotReceive()
            .QueryAsync(Arg.Any<QueryRequestDto>(), Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task PostQuery_WithQuestionExceeding2000Chars_Returns400ValidationError()
    {
        // Arrange
        var request = new { knowledge_base_id = "kb-001", question = new string('x', 2001) };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/query", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);

        await _factory.CoreApiClient
            .DidNotReceive()
            .QueryAsync(Arg.Any<QueryRequestDto>(), Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task PostQuery_WhenCoreApiThrowsHttpRequestException_Returns503()
    {
        // Arrange
        _factory.CoreApiClient
            .QueryAsync(Arg.Any<QueryRequestDto>(), Arg.Any<CancellationToken>())
            .ThrowsAsync(new HttpRequestException("Core service unavailable"));

        var request = new { knowledge_base_id = "kb-001", question = "What is the warranty period?" };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/query", request);

        // Assert - ErrorHandlingMiddleware maps HttpRequestException to 503
        response.StatusCode.Should().Be(HttpStatusCode.ServiceUnavailable);
    }

    [Fact]
    public async Task PostQuery_ForwardsCorrectPayloadToClient()
    {
        // Arrange
        var capturedRequest = (QueryRequestDto?)null;
        var interactionId = Guid.NewGuid().ToString();

        _factory.CoreApiClient
            .QueryAsync(Arg.Do<QueryRequestDto>(r => capturedRequest = r), Arg.Any<CancellationToken>())
            .Returns(new QueryResponseDto("answered", "Answer text", null, interactionId, null));

        var request = new { knowledge_base_id = "kb-abc", question = "How do I reset the device?" };

        // Act
        await _client.PostAsJsonAsync("/api/v1/query", request);

        // Assert - endpoint passes through what the client sends
        capturedRequest.Should().NotBeNull();
        capturedRequest!.KnowledgeBaseId.Should().Be("kb-abc");
        capturedRequest.Question.Should().Be("How do I reset the device?");
    }
}
