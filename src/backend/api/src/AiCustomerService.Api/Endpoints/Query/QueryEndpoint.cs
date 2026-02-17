namespace AiCustomerService.Api.Endpoints.Query;

using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;
using FastEndpoints;

public sealed class QueryEndpoint : Endpoint<QueryRequestDto, QueryResponseDto>
{
    private readonly ICoreApiClient _coreApi;

    public QueryEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Post("query");
        AllowAnonymous();
    }

    public override async Task HandleAsync(QueryRequestDto req, CancellationToken ct)
    {
        var result = await _coreApi.QueryAsync(req, ct);
        await SendAsync(result, cancellation: ct);
    }
}
