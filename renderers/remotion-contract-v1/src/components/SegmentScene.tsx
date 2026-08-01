import { AbsoluteFill, Img, staticFile } from "remotion";

import type { ContractSegment } from "../contract/types";

export const SegmentScene: React.FC<{ segment: ContractSegment }> = ({ segment }) => {
  const source = segment.visualRefs[0];
  return (
    <AbsoluteFill style={{ backgroundColor: "#10141b" }}>
      {source ? (
        <Img
          src={staticFile(source)}
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
        />
      ) : null}
    </AbsoluteFill>
  );
};
