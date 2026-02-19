using System.Net;
using System.Net.Http.Json;
using AiCustomerService.Api.Domain.Models;
using FluentAssertions;
using NSubstitute;
using Xunit;

namespace AiCustomerService.Api.Tests.Tests.Endpoints;

public sealed class KnowledgeBasesEndpointTests : IClassFixture<ApiTestFactory>
{
    private readonly ApiTestFactory _factory;
    private readonly HttpClient _client;

    public KnowledgeBasesEndpointTests(ApiTestFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
        // Clear any recorded calls from previous tests in this fixture
        _factory.CoreApiClient.ClearReceivedCalls();
    }

    // -------------------------------------------------------------------------
    // LIST
    // -------------------------------------------------------------------------

    [Fact]
    public async Task GetKnowledgeBases_Returns200WithList()
    {
        // Arrange
        var now = DateTime.UtcNow;
        var knowledgeBases = new List<KnowledgeBaseDto>
        {
            new("kb-001", "Product Manual KB", "Contains product manuals", now),
            new("kb-002", "FAQ KB", null, now),
        };

        _factory.CoreApiClient
            .ListKnowledgeBasesAsync(Arg.Any<CancellationToken>())
            .Returns(knowledgeBases);

        // Act
        var response = await _client.GetAsync("/api/v1/knowledge-bases");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<List<KnowledgeBaseDto>>();
        body.Should().NotBeNull();
        body.Should().HaveCount(2);
        body![0].Id.Should().Be("kb-001");
        body[0].Name.Should().Be("Product Manual KB");
        body[1].Id.Should().Be("kb-002");
        body[1].Description.Should().BeNull();
    }

    [Fact]
    public async Task GetKnowledgeBases_WhenNoneExist_Returns200WithEmptyArray()
    {
        // Arrange
        _factory.CoreApiClient
            .ListKnowledgeBasesAsync(Arg.Any<CancellationToken>())
            .Returns(new List<KnowledgeBaseDto>());

        // Act
        var response = await _client.GetAsync("/api/v1/knowledge-bases");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<List<KnowledgeBaseDto>>();
        body.Should().NotBeNull().And.BeEmpty();
    }

    // -------------------------------------------------------------------------
    // CREATE
    // -------------------------------------------------------------------------

    [Fact]
    public async Task PostKnowledgeBase_WithValidRequest_Returns201WithCreatedKb()
    {
        // Arrange
        var created = new KnowledgeBaseDto("kb-new", "Support KB", "Customer support documents", DateTime.UtcNow);

        _factory.CoreApiClient
            .CreateKnowledgeBaseAsync(Arg.Any<CreateKnowledgeBaseRequestDto>(), Arg.Any<CancellationToken>())
            .Returns(created);

        var request = new { name = "Support KB", description = "Customer support documents" };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/knowledge-bases", request);

        // Assert - CreateKnowledgeBaseEndpoint uses SendCreatedAtAsync which returns 201
        response.StatusCode.Should().Be(HttpStatusCode.Created);

        var body = await response.Content.ReadFromJsonAsync<KnowledgeBaseDto>();
        body.Should().NotBeNull();
        body!.Id.Should().Be("kb-new");
        body.Name.Should().Be("Support KB");
    }

    [Fact]
    public async Task PostKnowledgeBase_WithEmptyName_Returns400ValidationError()
    {
        // Arrange
        var request = new { name = "", description = "Some description" };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/knowledge-bases", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);

        await _factory.CoreApiClient
            .DidNotReceive()
            .CreateKnowledgeBaseAsync(Arg.Any<CreateKnowledgeBaseRequestDto>(), Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task PostKnowledgeBase_WithNameExceeding200Chars_Returns400ValidationError()
    {
        // Arrange
        var request = new { name = new string('a', 201), description = (string?)null };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/knowledge-bases", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task PostKnowledgeBase_ForwardsNameAndDescriptionToClient()
    {
        // Arrange
        var capturedRequest = (CreateKnowledgeBaseRequestDto?)null;
        var created = new KnowledgeBaseDto("kb-xyz", "My KB", "Desc text", DateTime.UtcNow);

        _factory.CoreApiClient
            .CreateKnowledgeBaseAsync(
                Arg.Do<CreateKnowledgeBaseRequestDto>(r => capturedRequest = r),
                Arg.Any<CancellationToken>())
            .Returns(created);

        var request = new { name = "My KB", description = "Desc text" };

        // Act
        await _client.PostAsJsonAsync("/api/v1/knowledge-bases", request);

        // Assert
        capturedRequest.Should().NotBeNull();
        capturedRequest!.Name.Should().Be("My KB");
        capturedRequest.Description.Should().Be("Desc text");
    }

    // -------------------------------------------------------------------------
    // GET by ID
    // -------------------------------------------------------------------------

    [Fact]
    public async Task GetKnowledgeBase_WithValidId_Returns200WithKb()
    {
        // Arrange
        var kb = new KnowledgeBaseDto("kb-001", "Product Manual KB", null, DateTime.UtcNow);

        _factory.CoreApiClient
            .GetKnowledgeBaseAsync("kb-001", Arg.Any<CancellationToken>())
            .Returns(kb);

        // Act
        var response = await _client.GetAsync("/api/v1/knowledge-bases/kb-001");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<KnowledgeBaseDto>();
        body.Should().NotBeNull();
        body!.Id.Should().Be("kb-001");
        body.Name.Should().Be("Product Manual KB");
    }

    [Fact]
    public async Task GetKnowledgeBase_PassesCorrectIdToClient()
    {
        // Arrange
        var capturedId = string.Empty;
        var kb = new KnowledgeBaseDto("kb-abc", "Test KB", null, DateTime.UtcNow);

        _factory.CoreApiClient
            .GetKnowledgeBaseAsync(
                Arg.Do<string>(id => capturedId = id),
                Arg.Any<CancellationToken>())
            .Returns(kb);

        // Act
        await _client.GetAsync("/api/v1/knowledge-bases/kb-abc");

        // Assert
        capturedId.Should().Be("kb-abc");
    }

    // -------------------------------------------------------------------------
    // DELETE
    // -------------------------------------------------------------------------

    [Fact]
    public async Task DeleteKnowledgeBase_WithValidId_Returns204()
    {
        // Arrange
        _factory.CoreApiClient
            .DeleteKnowledgeBaseAsync("kb-001", Arg.Any<CancellationToken>())
            .Returns(Task.CompletedTask);

        // Act
        var response = await _client.DeleteAsync("/api/v1/knowledge-bases/kb-001");

        // Assert - DeleteKnowledgeBaseEndpoint uses SendNoContentAsync = 204
        response.StatusCode.Should().Be(HttpStatusCode.NoContent);
    }

    [Fact]
    public async Task DeleteKnowledgeBase_PassesCorrectIdToClient()
    {
        // Arrange
        var capturedId = string.Empty;

        _factory.CoreApiClient
            .DeleteKnowledgeBaseAsync(
                Arg.Do<string>(id => capturedId = id),
                Arg.Any<CancellationToken>())
            .Returns(Task.CompletedTask);

        // Act
        await _client.DeleteAsync("/api/v1/knowledge-bases/kb-to-delete");

        // Assert
        capturedId.Should().Be("kb-to-delete");
    }
}
