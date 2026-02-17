namespace AiCustomerService.Api.Endpoints.Documents;

using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;
using FastEndpoints;
using Microsoft.AspNetCore.Http;

public sealed class UploadDocumentRequest
{
    public IFormFile File { get; set; } = null!;
}

public sealed class UploadDocumentEndpoint : Endpoint<UploadDocumentRequest, DocumentDto>
{
    private readonly ICoreApiClient _coreApi;

    public UploadDocumentEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Post("knowledge-bases/{kbId}/documents");
        AllowAnonymous();
        AllowFileUploads();
    }

    public override async Task HandleAsync(UploadDocumentRequest req, CancellationToken ct)
    {
        var kbId = Route<string>("kbId")!;
        using var stream = req.File.OpenReadStream();
        var result = await _coreApi.UploadDocumentAsync(kbId, stream, req.File.FileName, ct);
        await SendCreatedAtAsync("", null, result, cancellation: ct);
    }
}
