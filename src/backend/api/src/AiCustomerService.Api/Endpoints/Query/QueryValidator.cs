namespace AiCustomerService.Api.Endpoints.Query;

using AiCustomerService.Api.Domain.Models;
using FastEndpoints;
using FluentValidation;

public sealed class QueryValidator : Validator<QueryRequestDto>
{
    public QueryValidator()
    {
        RuleFor(x => x.KnowledgeBaseId)
            .NotEmpty().WithMessage("Knowledge base ID is required");

        RuleFor(x => x.Question)
            .NotEmpty().WithMessage("Question is required")
            .MaximumLength(2000).WithMessage("Question must not exceed 2000 characters");
    }
}
