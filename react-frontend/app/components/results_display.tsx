import { Corporation, FilingInfo } from "../api/search";

function getFilingValue(filings: FilingInfo[], id: string) {
  return filings.find((f: FilingInfo) => f["internal_name"] == id)?.value || 'N/A';
}

export default function ResultsDisplay({ results }: { results: Corporation[] }) {
  if (!results || results.length === 0) {
    return null;
  }
  return (
    <div className="mt-6 grid gap-6 sm:grid-cols-1 md:grid-cols-1 lg:grid-cols-1">
      {results.map((business) => (
        <div
          key={business.id}
          className="bg-foreground text-background shadow rounded-lg p-6 border border-gray-200"
        >
          <h2 className="text-xl font-bold mb-2">{business.name}</h2>
          <p className="text-gray-600 mb-2">
            <strong>Type:</strong> {business.type}
          </p>

          <div className="mb-2">
            <strong>Registered Address:</strong>
            <p className="whitespace-pre-wrap text-sm">
              {business.registered_addr}
            </p>
          </div>
          <div className="mb-2">
            <strong>Principal Address:</strong>
            <p className="whitespace-pre-wrap text-sm">
              {business.principal_addr}
            </p>
          </div>
          <div className="mb-2">
            <strong>Mailing Address:</strong>
            <p className="whitespace-pre-wrap text-sm">
              {business.mailing_addr}
            </p>
          </div>
          <div className="mb-2">
            <strong>Registered Name:</strong> {business.registered_name}
          </div>
          <div className="mb-2">
            <strong>Document Number:</strong>{' '}
            {getFilingValue(business.filing_info, 'Detail_DocumentId')}
          </div>
          <div className="mb-2">
            <strong>Filing Date:</strong>{' '}
            {getFilingValue(business.filing_info, 'Detail_FileDate')}
          </div>
          <div className="mb-2">
            <strong>Status:</strong>{' '}
            {getFilingValue(business.filing_info, 'Detail_Status')}
          </div>

          <div className="mb-2">
            <strong>Officers:</strong>
            <ul className="list-disc list-inside text-sm">
              {business.officers && business.officers.length > 0 ? (
                business.officers.map((officer) => (
                  <li key={officer.id}>{officer.name} ({officer.title})</li>
                ))
              ) : (
                <li>N/A</li>
              )}
            </ul>
          </div>

          <div className="mb-2">
            <strong>Annual Report:</strong>
            <p className="text-sm">
              {business.annual_reports && business.annual_reports.length > 0
                ? `${business.annual_reports[0].filing_date} (${business.annual_reports[0].report_year})`
                : 'N/A'}
            </p>
          </div>

          <div className="mb-2">
            <strong>Documents:</strong>
            <ul className="list-disc list-inside text-sm">
              {business.documents && business.documents.length > 0 ? (
                business.documents.map((doc) => (
                  <li key={doc.id}>
                    <a
                      href={doc.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline"
                    >
                      {doc.title}
                    </a>
                  </li>
                ))
              ) : (
                <li>N/A</li>
              )}
            </ul>
          </div>
        </div>
      ))}
    </div>
  );
}
